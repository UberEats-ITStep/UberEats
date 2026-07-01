from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'created_at', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'phone_number', 'address']

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
            role=validated_data.get('role', 'Client')
        )
        user.profile.phone_number = phone_number or None
        user.profile.address = address or None
        user.profile.save()
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email', '')
        if not User.objects.filter(email=email).exists():
            raise AuthenticationFailed('No account found with this email.')

        try:
            return super().validate(attrs)
        except AuthenticationFailed as error:
            raise AuthenticationFailed('Incorrect password.') from error
