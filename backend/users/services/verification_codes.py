import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from users.models import User, VerificationCode


class VerificationCodeCooldownError(Exception):
    pass


class VerificationCodeService:
    @staticmethod
    def issue_code(user: User, purpose: str) -> str:
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user.pk)
            now = timezone.now()
            VerificationCodeService.delete_expired_codes(user, purpose, now)

            latest_code = (
                VerificationCode.objects.filter(user=user, purpose=purpose)
                .order_by('-created_at')
                .first()
            )
            if latest_code is not None and not VerificationCodeService.can_resend(
                latest_code, purpose, now
            ):
                raise VerificationCodeCooldownError

            VerificationCode.objects.filter(user=user, purpose=purpose).delete()

            code = VerificationCodeService.generate_code()
            VerificationCode.objects.create(
                user=user,
                code_hash=make_password(code),
                purpose=purpose,
                expires_at=now + timedelta(
                    seconds=VerificationCodeService.get_expiration_seconds(purpose)
                ),
            )
            return code

    @staticmethod
    def consume_code(user: User, purpose: str, code: str) -> bool:
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user.pk)
            now = timezone.now()
            VerificationCodeService.delete_expired_codes(user, purpose, now)
            verification_code = (
                VerificationCode.objects.select_for_update()
                .filter(user=user, purpose=purpose)
                .order_by('-created_at')
                .first()
            )
            if verification_code is None:
                return False
            if not check_password(code, verification_code.code_hash):
                return False

            verification_code.delete()
            return True

    @staticmethod
    def delete_expired_codes(
        user: User, purpose: str, current_time=None
    ) -> None:
        current_time = current_time or timezone.now()
        VerificationCode.objects.filter(
            user=user,
            purpose=purpose,
            expires_at__lte=current_time,
        ).delete()

    @staticmethod
    def generate_code() -> str:
        return str(secrets.randbelow(900000) + 100000)

    @staticmethod
    def can_resend(
        verification_code: VerificationCode, purpose: str, current_time=None
    ) -> bool:
        current_time = current_time or timezone.now()
        cooldown = timedelta(
            seconds=VerificationCodeService.get_cooldown_seconds(purpose)
        )
        return verification_code.created_at + cooldown <= current_time

    @staticmethod
    def get_expiration_seconds(purpose: str) -> int:
        if purpose == VerificationCode.Purpose.PASSWORD_RESET:
            return settings.PASSWORD_RESET_CODE_TTL_SECONDS
        raise ValueError('Unsupported verification code purpose.')

    @staticmethod
    def get_cooldown_seconds(purpose: str) -> int:
        if purpose == VerificationCode.Purpose.PASSWORD_RESET:
            return settings.PASSWORD_RESET_RESEND_COOLDOWN_SECONDS
        raise ValueError('Unsupported verification code purpose.')