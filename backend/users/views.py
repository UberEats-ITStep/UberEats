from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User
from .serializers import (
    EmailTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)
from .services.password_reset import PasswordResetService

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
    throttle_scope = 'auth_register'


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    throttle_scope = 'auth_login'


class ForgotPasswordView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'password_reset_request'

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService.request_reset(serializer.validated_data['email'])
        return Response(
            {'detail': 'If an account exists, a reset code has been sent.'},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'password_reset_confirm'

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password_reset = PasswordResetService.reset_password(
            serializer.validated_data['email'],
            serializer.validated_data['verification_code'],
            serializer.validated_data['new_password'],
        )
        if not password_reset:
            return Response(
                {'detail': 'The verification code is invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'detail': 'Password reset successful.'},
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = 'change_password'

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        return Response(
            {
                "detail": "Password changed successfully. Please log in again."
            },
            status=status.HTTP_200_OK
        )
from .services.email_verification import verify_user_code, generate_verification_code, send_verification_email

class VerifyEmailView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'verify_email'

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({'detail': 'Email and code are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({'detail': 'No account found with this email.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            verify_user_code(user, code)
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully.',
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_scope = 'resend_verification'

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            # Silently return success to avoid email enumeration
            return Response({'message': 'Verification email sent.'}, status=status.HTTP_200_OK)
            
        if user.is_verified:
            return Response({'detail': 'Email already verified.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            plaintext_code = generate_verification_code(user)
            send_verification_email(user, plaintext_code)
            return Response({'message': 'Verification email sent.'}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
