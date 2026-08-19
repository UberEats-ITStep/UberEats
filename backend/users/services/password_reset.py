import logging

from django.db import transaction

from users.models import User, VerificationCode

from .email_service import EmailService
from .verification_codes import (
    VerificationCodeCooldownError,
    VerificationCodeService,
)


logger = logging.getLogger(__name__)


class PasswordResetService:
    @staticmethod
    def request_reset(email: str) -> None:
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return

        try:
            code = VerificationCodeService.issue_code(
                user,
                VerificationCode.Purpose.PASSWORD_RESET,
            )
        except VerificationCodeCooldownError:
            return

        try:
            email_sent = EmailService.send_password_reset_code(user, code)
        except Exception:
            logger.exception('Unable to send password reset email.')
            email_sent = False

        if not email_sent:
            VerificationCodeService.delete_codes(
                user,
                VerificationCode.Purpose.PASSWORD_RESET,
            )

    @staticmethod
    @transaction.atomic
    def reset_password(email: str, code: str, new_password: str) -> bool:
        user = User.objects.select_for_update().filter(email__iexact=email).first()
        if user is None:
            return False

        code_is_valid = VerificationCodeService.consume_code(
            user,
            VerificationCode.Purpose.PASSWORD_RESET,
            code,
        )
        if not code_is_valid:
            return False

        user.set_password(new_password)
        user.save(update_fields=['password'])
        return True