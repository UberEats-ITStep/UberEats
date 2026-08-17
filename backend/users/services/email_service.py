from django.conf import settings
from django.core.mail import send_mail


class EmailService:
    @staticmethod
    def send_password_reset_code(email: str, code: str) -> bool:
        return send_mail(
            subject='Password reset code',
            message=f'Your password reset verification code is: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        ) == 1