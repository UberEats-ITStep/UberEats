from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Profile


PHONE_NUMBER_VALIDATOR = RegexValidator(
    regex=r'^\+[1-9]\d{7,14}$',
    message=(
        'Enter a valid phone number in international format, '
        'for example +380501234567.'
    ),
)


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
        ]

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
