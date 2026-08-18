import re
from datetime import timedelta
from typing import Any, cast
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework.throttling import ScopedRateThrottle

from .models import Profile, VerificationCode


# Start PostgreSQL before running these tests; the backend test suite expects the real database.
UserModel: Any = get_user_model()


class UserModelTests(TestCase):
    def test_user_creation_creates_profile(self) -> None:
        user = cast(
            Any,
            UserModel.objects.create_user(
                username='john',
                email='john@example.com',
                password='pass12345',
                role='Courier',
            ),
        )

        self.assertIsNotNone(user.created_at)
        self.assertEqual(user.role, 'Courier')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.user, user)

    def test_user_save_keeps_single_profile(self) -> None:
        user = cast(
            Any,
            UserModel.objects.create_user(
                username='jane',
                email='jane@example.com',
                password='pass12345',
            ),
        )

        profile_id = user.profile.id
        user.first_name = 'Jane'
        user.save()

        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        self.assertEqual(user.profile.id, profile_id)

    def test_profile_string_representation_uses_email(self) -> None:
        user = cast(
            Any,
            UserModel.objects.create_user(
                username='alex',
                email='alex@example.com',
                password='pass12345',
            ),
        )

        self.assertEqual(str(user.profile), 'alex@example.com Profile')


class RegisterApiTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('register')

    def test_register_creates_user_profile_and_unique_username(self) -> None:
        UserModel.objects.create_user(
            username='test.user',
            email='existing@example.com',
            password='pass12345',
        )

        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    'email': 'test.user@example.com',
                    'password': 'TestPass123!',
                    'role': 'CLIENT',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'test.user@example.com')
        self.assertEqual(response.data['role'], 'CLIENT')

        user = cast(Any, UserModel.objects.get(email='test.user@example.com'))
        self.assertEqual(user.username, 'test.user1')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_saves_optional_profile_fields(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    'email': 'profile@example.com',
                    'password': 'TestPass123!',
                    'role': 'CLIENT',
                    'phone_number': '+380000000000',
                    'address': 'Kyiv',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = cast(Any, UserModel.objects.get(email='profile@example.com'))
        self.assertEqual(user.profile.phone_number, '+380000000000')
        self.assertEqual(user.profile.address, 'Kyiv')

    def test_register_rejects_invalid_phone_number(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    'email': 'invalid-phone@example.com',
                    'password': 'TestPass123!',
                    'phone_number': '050-123',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('international format', str(response.data['phone_number'][0]))
        self.assertFalse(UserModel.objects.filter(email='invalid-phone@example.com').exists())

    def test_register_existing_email_returns_clear_error(self) -> None:
        UserModel.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='TestPass123!',
        )

        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    'email': 'existing@example.com',
                    'password': 'TestPass123!',
                    'role': 'CLIENT',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', str(response.data['email'][0]))


class JwtAuthApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = cast(
            Any,
            UserModel.objects.create_user(
                username='john',
                email='john@example.com',
                password='TestPass123!',
                role='CLIENT',
            ),
        )
        self.login_url = reverse('login')
        self.refresh_url = reverse('token_refresh')
        self.profile_url = reverse('profile')

    def authenticate(self) -> dict[str, str]:
        login_response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': 'john@example.com',
                    'password': 'TestPass123!',
                },
                format='json',
            ),
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        return cast(dict[str, str], login_response.data)

    def test_login_returns_access_and_refresh_tokens(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': 'john@example.com',
                    'password': 'TestPass123!',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_unknown_email_returns_clear_error(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': 'missing@example.com',
                    'password': 'TestPass123!',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'No account found with this email.')

    def test_login_wrong_password_returns_clear_error(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': 'john@example.com',
                    'password': 'WrongPass123!',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Incorrect password.')

    def test_refresh_returns_new_access_token(self) -> None:
        login_data = self.authenticate()

        response = cast(
            Response,
            self.client.post(
                self.refresh_url,
                {'refresh': login_data['refresh']},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_requires_authentication(self) -> None:
        response = cast(Response, self.client.get(self.profile_url))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_requires_authentication(self) -> None:
        response = cast(
            Response,
            self.client.patch(
                self.profile_url, {'address': 'Kyiv'}, format='json'
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.user.profile.refresh_from_db()
        self.assertIsNone(self.user.profile.address)

    def test_profile_can_be_read_and_updated_with_jwt(self) -> None:
        login_data = self.authenticate()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_data['access']}")

        get_response = cast(Response, self.client.get(self.profile_url))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['id'], self.user.id)
        self.assertEqual(get_response.data['email'], 'john@example.com')
        self.assertEqual(get_response.data['role'], 'CLIENT')
        self.assertIsNone(get_response.data['phone_number'])
        self.assertIsNone(get_response.data['address'])

        patch_response = cast(
            Response,
            self.client.patch(
                self.profile_url,
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone_number': '+380000000000',
                    'address': 'Kyiv',
                },
                format='json',
            ),
        )

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['first_name'], 'John')
        self.assertEqual(patch_response.data['last_name'], 'Doe')
        self.assertEqual(patch_response.data['phone_number'], '+380000000000')
        self.assertEqual(patch_response.data['address'], 'Kyiv')

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.profile.phone_number, '+380000000000')
        self.assertEqual(self.user.profile.address, 'Kyiv')

    def test_profile_rejects_invalid_phone_number_with_clear_error(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                self.profile_url, {'phone_number': '050-123'}, format='json'
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('international format', str(response.data['phone_number'][0]))

    def test_profile_rejects_blank_delivery_fields(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                self.profile_url,
                {'phone_number': '', 'address': ''},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['phone_number'][0]), 'This field may not be blank.')
        self.assertEqual(str(response.data['address'][0]), 'This field may not be blank.')

    def test_full_profile_update_reports_missing_required_email(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.put(
                self.profile_url, {'first_name': 'John'}, format='json'
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['email'][0]), 'This field is required.')

    def test_profile_rejects_duplicate_email(self) -> None:
        UserModel.objects.create_user(
            username='jane',
            email='jane@example.com',
            password='TestPass123!',
        )
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                self.profile_url, {'email': 'JANE@example.com'}, format='json'
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already exists', str(response.data['email'][0]))

    def test_profile_does_not_allow_identity_or_role_changes(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                self.profile_url,
                {'id': 999, 'username': 'hacker', 'role': 'ADMIN'},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.id, 999)
        self.assertEqual(self.user.username, 'john')
        self.assertEqual(self.user.role, 'CLIENT')

    def test_profile_endpoint_always_uses_authenticated_users_profile(self) -> None:
        other_user = cast(
            Any,
            UserModel.objects.create_user(
                username='jane',
                email='jane@example.com',
                password='TestPass123!',
            ),
        )
        other_user.profile.address = 'Lviv'
        other_user.profile.save()
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                self.profile_url, {'address': 'Kyiv'}, format='json'
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        other_user.profile.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(other_user.profile.address, 'Lviv')
        self.assertEqual(self.user.profile.address, 'Kyiv')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    PASSWORD_RESET_CODE_TTL_SECONDS=600,
    PASSWORD_RESET_RESEND_COOLDOWN_SECONDS=60,
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_RATES': {
            'password_reset_request': '100/hour',
            'password_reset_confirm': '100/hour',
        },
    },
)
class PasswordResetApiTests(APITestCase):
    def setUp(self) -> None:
        cache.clear()
        mail.outbox = []
        self.user = cast(
            Any,
            UserModel.objects.create_user(
                username='reset.user',
                email='reset@example.com',
                password='CurrentPass123!',
            ),
        )
        self.forgot_password_url = reverse('forgot-password')
        self.reset_password_url = reverse('reset-password')
        self.login_url = reverse('login')

    def get_verification_code(self, message: Any) -> str:
        match = re.search(r'\b(\d{6})\b', message.body)
        self.assertIsNotNone(match)
        return cast(Any, match).group(1)

    def request_reset_code(self) -> str:
        response = cast(
            Response,
            self.client.post(
                self.forgot_password_url,
                {'email': self.user.email},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        return self.get_verification_code(mail.outbox[0])

    def reset_password(self, code: str, password: str = 'UpdatedPass123!') -> Response:
        return cast(
            Response,
            self.client.post(
                self.reset_password_url,
                {
                    'email': self.user.email,
                    'verification_code': code,
                    'new_password': password,
                    'confirm_password': password,
                },
                format='json',
            ),
        )

    def test_forgot_password_returns_same_response_for_existing_and_missing_email(self) -> None:
        existing_response = cast(
            Response,
            self.client.post(
                self.forgot_password_url,
                {'email': self.user.email},
                format='json',
            ),
        )
        missing_response = cast(
            Response,
            self.client.post(
                self.forgot_password_url,
                {'email': 'missing@example.com'},
                format='json',
            ),
        )

        self.assertEqual(existing_response.status_code, status.HTTP_200_OK)
        self.assertEqual(missing_response.status_code, status.HTTP_200_OK)
        self.assertEqual(existing_response.data, missing_response.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_updates_password_and_removes_code(self) -> None:
        code = self.request_reset_code()
        verification_code = VerificationCode.objects.get(
            user=self.user,
            purpose=VerificationCode.Purpose.PASSWORD_RESET,
        )

        self.assertNotEqual(verification_code.code_hash, code)

        response = self.reset_password(code)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            VerificationCode.objects.filter(
                user=self.user,
                purpose=VerificationCode.Purpose.PASSWORD_RESET,
            ).exists()
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('UpdatedPass123!'))
        self.assertFalse(self.user.check_password('CurrentPass123!'))

        old_password_response = cast(
            Response,
            self.client.post(
                self.login_url,
                {'email': self.user.email, 'password': 'CurrentPass123!'},
                format='json',
            ),
        )
        new_password_response = cast(
            Response,
            self.client.post(
                self.login_url,
                {'email': self.user.email, 'password': 'UpdatedPass123!'},
                format='json',
            ),
        )

        self.assertEqual(old_password_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(new_password_response.status_code, status.HTTP_200_OK)

    def test_reset_password_rejects_invalid_code(self) -> None:
        self.request_reset_code()

        response = self.reset_password('000000')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('CurrentPass123!'))

    def test_reset_password_removes_expired_code(self) -> None:
        code = self.request_reset_code()
        verification_code = VerificationCode.objects.get(user=self.user)
        verification_code.expires_at = timezone.now() - timedelta(seconds=1)
        verification_code.save(update_fields=['expires_at'])

        response = self.reset_password(code)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(VerificationCode.objects.filter(user=self.user).exists())

    def test_forgot_password_enforces_resend_cooldown(self) -> None:
        self.request_reset_code()
        verification_code = VerificationCode.objects.get(user=self.user)

        response = cast(
            Response,
            self.client.post(
                self.forgot_password_url,
                {'email': self.user.email},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(VerificationCode.objects.get(user=self.user).pk, verification_code.pk)

    def test_forgot_password_invalidates_previous_code_after_cooldown(self) -> None:
        first_code = self.request_reset_code()
        verification_code = VerificationCode.objects.get(user=self.user)
        verification_code.created_at = timezone.now() - timedelta(seconds=61)
        verification_code.save(update_fields=['created_at'])

        response = cast(
            Response,
            self.client.post(
                self.forgot_password_url,
                {'email': self.user.email},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)

        invalid_response = self.reset_password(first_code)

        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'password_reset_request': '2/hour',
                'password_reset_confirm': '2/hour',
            },
        },
    )
    @patch.object(
        ScopedRateThrottle,
        'THROTTLE_RATES',
        {
            'password_reset_request': '2/hour',
            'password_reset_confirm': '2/hour',
        },
    )
    def test_forgot_password_throttling(self) -> None:
        for _ in range(2):
            response = cast(
                Response,
                self.client.post(
                    self.forgot_password_url,
                    {'email': self.user.email},
                    format='json',
                ),
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        throttled_response = cast(
            Response,
            self.client.post(
                self.forgot_password_url,
                {'email': self.user.email},
                format='json',
            ),
        )

        self.assertEqual(throttled_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'password_reset_request': '2/hour',
                'password_reset_confirm': '2/hour',
            },
        },
    )
    @patch.object(
        ScopedRateThrottle,
        'THROTTLE_RATES',
        {
            'password_reset_request': '2/hour',
            'password_reset_confirm': '2/hour',
        },
    )
    def test_reset_password_throttling(self) -> None:
        self.request_reset_code()

        for _ in range(2):
            response = self.reset_password('000000')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        throttled_response = self.reset_password('000000')

        self.assertEqual(throttled_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class ChangePasswordApiTests(APITestCase):
    def setUp(self) -> None:
        cache.clear()
        self.user = cast(
            Any,
            UserModel.objects.create_user(
                username='change.password.user',
                email='change@example.com',
                password='CurrentPass123!',
                role='CLIENT',
            ),
        )

        self.change_password_url = reverse('change-password')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')

    def authenticate(self) -> dict[str, str]:
        response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': self.user.email,
                    'password': 'CurrentPass123!',
                },
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        return cast(dict[str, str], response.data)

    def change_password(
        self,
        access_token: str,
        refresh_token: str,
        current_password: str = 'CurrentPass123!',
        new_password: str = 'NewPassword123!',
        confirm_password: str = 'NewPassword123!',
    ) -> Response:
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        return cast(
            Response,
            self.client.post(
                self.change_password_url,
                {
                    'current_password': current_password,
                    'new_password': new_password,
                    'confirm_password': confirm_password,
                    'refresh_token': refresh_token,
                },
                format='json',
            ),
        )

    def test_change_password_successfully(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['detail'],
            'Password changed successfully. Please log in again.',
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('NewPassword123!')
        )
        self.assertFalse(
            self.user.check_password('CurrentPass123!')
        )

    def test_change_password_rejects_incorrect_current_password(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
            current_password='WrongPassword123!',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'current_password',
            response.data,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password('CurrentPass123!')
        )

    def test_change_password_rejects_mismatched_passwords(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
            new_password='NewPassword123!',
            confirm_password='DifferentPassword123!',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'confirm_password',
            response.data,
        )

    def test_change_password_rejects_invalid_new_password(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
            new_password='123',
            confirm_password='123',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'non_field_errors',
            response.data,
        )

    def test_change_password_rejects_same_password(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
            new_password='CurrentPass123!',
            confirm_password='CurrentPass123!',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn(
            'new_password',
            response.data,
        )

    def test_change_password_requires_authentication(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.change_password_url,
                {
                    'current_password': 'CurrentPass123!',
                    'new_password': 'NewPassword123!',
                    'confirm_password': 'NewPassword123!',
                    'refresh_token': 'invalid',
                },
                format='json',
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_old_password_no_longer_works_after_change(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        old_password_response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': self.user.email,
                    'password': 'CurrentPass123!',
                },
                format='json',
            ),
        )

        self.assertEqual(
            old_password_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_new_password_allows_login(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        new_password_response = cast(
            Response,
            self.client.post(
                self.login_url,
                {
                    'email': self.user.email,
                    'password': 'NewPassword123!',
                },
                format='json',
            ),
        )

        self.assertEqual(
            new_password_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn('access', new_password_response.data)
        self.assertIn('refresh', new_password_response.data)

    def test_refresh_token_is_blacklisted_after_password_change(self) -> None:
        login_data = self.authenticate()

        response = self.change_password(
            login_data['access'],
            login_data['refresh'],
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        refresh_response = cast(
            Response,
            self.client.post(
                reverse('token_refresh'),
                {
                    'refresh': login_data['refresh'],
                },
                format='json',
            ),
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_RATES': {
                'change_password': '2/hour',
            },
        },
    )
    @patch.object(
        ScopedRateThrottle,
        'THROTTLE_RATES',
        {
            'change_password': '2/hour',
        },
    )

    def test_change_password_throttling(self) -> None:
        login_data = self.authenticate()

        for _ in range(2):
            response = self.change_password(
                login_data['access'],
                login_data['refresh'],
                current_password='WrongPassword123!',
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
            )

        throttled_response = self.change_password(
            login_data['access'],
            login_data['refresh'],
            current_password='WrongPassword123!',
        )

        self.assertEqual(
            throttled_response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )