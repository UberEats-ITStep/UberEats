from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import DeliveryAddress, Profile, User


PHONE_NUMBER_VALIDATOR = RegexValidator(
    regex=r'^\+[1-9]\d{7,14}$',
    message=(
        'Enter a valid phone number in international format, '
        'for example +380501234567.'
    ),
)


class DeliveryAddressSerializer(serializers.ModelSerializer):
    floor = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=100,
    )
    contact_phone = serializers.CharField(
        max_length=16,
        required=False,
        allow_blank=True,
        validators=[PHONE_NUMBER_VALIDATOR],
    )

    class Meta:
        model = DeliveryAddress
        fields = [
            'id',
            'label',
            'formatted_address',
            'street',
            'building',
            'apartment',
            'entrance',
            'floor',
            'delivery_notes',
            'contact_phone',
            'latitude',
            'longitude',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'is_default',
            'created_at',
            'updated_at',
        ]

    def validate_label(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Label cannot be empty.')
        return value

    def validate_street(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Street cannot be empty.')
        return value

    def validate_building(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Building cannot be empty.')
        return value

    def validate_contact_phone(self, value):
        return value.strip()

    def validate(self, attrs):
        instance = self.instance

        if instance is None:
            missing_fields = {
                field: 'This field is required.'
                for field in ('street', 'building')
                if not attrs.get(field)
            }
            if missing_fields:
                raise serializers.ValidationError(missing_fields)

        latitude = attrs.get(
            'latitude',
            instance.latitude if instance is not None else None,
        )
        longitude = attrs.get(
            'longitude',
            instance.longitude if instance is not None else None,
        )

        if (latitude is None) != (longitude is None):
            missing_field = 'longitude' if longitude is None else 'latitude'
            raise serializers.ValidationError({
                missing_field: 'Latitude and longitude must both be set, or both be empty.'
            })

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(
        source='user.first_name', max_length=150, required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source='user.last_name', max_length=150, required=False, allow_blank=True
    )
    role = serializers.CharField(source='user.role', read_only=True)
    created_at = serializers.DateTimeField(source='user.created_at', read_only=True)
    phone_number = serializers.CharField(
        max_length=16,
        required=False,
        validators=[PHONE_NUMBER_VALIDATOR],
    )
    address = serializers.CharField(
        max_length=500,
        required=False,
    )
    default_address = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'created_at',
            'phone_number',
            'address',
            'avatar',
            'default_address',
        ]

    def get_default_address(self, instance):
        default_address = instance.user.delivery_addresses.filter(
            is_default=True
        ).first()
        if default_address is None:
            return None
        return DeliveryAddressSerializer(default_address).data

    def validate_email(self, value):
        email = value.lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return email

    @transaction.atomic
    def update(self, instance, validated_data):
        # User and Profile are separate tables. If either save fails, roll back both.
        user_data = validated_data.pop('user', {})
        for field, value in user_data.items():
            setattr(instance.user, field, value)
        if user_data:
            instance.user.save(update_fields=list(user_data))

        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at', 'profile']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=16,
        validators=[PHONE_NUMBER_VALIDATOR],
    )
    address = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=500,
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'phone_number', 'address']

    @transaction.atomic
    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number', '')
        address = validated_data.pop('address', '')
        email = validated_data['email']
        # A username from the email prefix so the frontend doesn't need it
        username = email.split('@')[0]
        
        # Ensure the generated username is unique just in case
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            role=validated_data.get('role', 'CLIENT')
        )
        user.profile.phone_number = phone_number or None
        user.profile.address = address or None
        user.profile.save()
        
        # Generate and send verification email
        from .services.email_verification import generate_verification_code, send_verification_email
        plaintext_code = generate_verification_code(user)
        try:
            send_verification_email(user, plaintext_code)
        except ValueError as e:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': str(e)})
            
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.RegexField(
        regex=r'^\d{6}$',
        write_only=True,
    )
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {'confirm_password': 'Passwords do not match.'}
            )

        user = User.objects.filter(email__iexact=attrs['email']).first()
        try:
            validate_password(attrs['new_password'], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {'new_password': list(error.messages)}
            ) from error

        return attrs


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email', '')
        user_queryset = User.objects.filter(email=email)
        
        if not user_queryset.exists():
            raise AuthenticationFailed('No account found with this email.')
            
        user = user_queryset.first()
        if not user.is_verified:
            raise AuthenticationFailed('Your email has not been verified yet. Please verify your email before logging in.')

        try:
            return super().validate(attrs)
        except AuthenticationFailed as error:
            raise AuthenticationFailed('Incorrect password.') from error


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True,
    )
    new_password = serializers.CharField(
        write_only=True,
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if not self.context["request"].user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({
                "current_password": "Incorrect password"
            })        
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        if attrs["current_password"] == attrs["new_password"]:
                    raise serializers.ValidationError({
                        "new_password": "New password is the same as old"
                    })

        validate_password(
            attrs["new_password"],
            self.context["request"].user
        )
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        password = self.validated_data["new_password"]
        user.set_password(password)
        user.save()
