from importlib import import_module
import re
from datetime import timedelta
from typing import Any, cast
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.apps import apps
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework.throttling import ScopedRateThrottle

from .models import DeliveryAddress, Profile, VerificationCode


# Start PostgreSQL before running these tests; the backend test suite expects the real database.
UserModel: Any = get_user_model()


class UserModelTests(TestCase):
    def test_user_creation_creates_profile(self) -> None:
        user = cast(
            Any,
            UserModel.objects.create_user(
                username='john',
                email='john@example.com',
                password='pass12345', is_verified=True,
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
                password='pass12345', is_verified=True,
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
                password='pass12345', is_verified=True,
            ),
        )

        self.assertEqual(str(user.profile), 'alex@example.com Profile')


class DeliveryAddressMigrationTests(TestCase):
    def test_legacy_profile_address_becomes_default_home_address(self) -> None:
        user = cast(
            Any,
            UserModel.objects.create_user(
                username='legacy-address-user',
                email='legacy-address@example.com',
                password='TestPass123!',
                is_verified=True,
            ),
        )
        user.profile.address = 'Rivne, Soborna Street 12'
        user.profile.save(update_fields=['address'])

        migration = import_module(
            'users.migrations.0008_migrate_profile_addresses'
        )
        migration.migrate_legacy_profile_addresses(apps, None)

        address = DeliveryAddress.objects.get(user=user)
        self.assertEqual(address.label, 'Home')
        self.assertEqual(address.formatted_address, 'Rivne, Soborna Street 12')
        self.assertEqual(address.street, '')
        self.assertEqual(address.building, '')
        self.assertIsNone(address.latitude)
        self.assertIsNone(address.longitude)
        self.assertTrue(address.is_default)


class RegisterApiTests(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('register')

    def test_register_creates_user_profile_and_unique_username(self) -> None:
        UserModel.objects.create_user(
            username='test.user',
            email='existing@example.com',
            password='pass12345', is_verified=True,
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
            password='TestPass123!', is_verified=True,
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
                password='TestPass123!', is_verified=True,
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
            password='TestPass123!', is_verified=True,
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
                password='TestPass123!', is_verified=True,
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


class SavedDeliveryAddressApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = cast(
            Any,
            UserModel.objects.create_user(
                username='address-owner',
                email='address-owner@example.com',
                password='TestPass123!',
                is_verified=True,
            ),
        )
        self.other_user = cast(
            Any,
            UserModel.objects.create_user(
                username='other-address-owner',
                email='other-address-owner@example.com',
                password='TestPass123!',
                is_verified=True,
            ),
        )
        self.list_url = reverse('delivery-address-list')
        self.default_url = reverse('delivery-address-default')
        self.profile_url = reverse('profile')
        self.avatar_options_url = reverse('avatar-options')

    def address_data(self, **overrides: Any) -> dict[str, Any]:
        data = {
            'label': 'Home',
            'formatted_address': 'Rivne, Soborna Street 12',
            'street': 'Soborna Street',
            'building': '12',
            'apartment': '44',
            'entrance': '2',
            'floor': 3,
            'delivery_notes': 'Call when near',
            'contact_phone': '+380501234567',
            'latitude': '50.619000',
            'longitude': '26.250000',
        }
        data.update(overrides)
        return data

    def create_address(self, **overrides: Any) -> Response:
        self.client.force_authenticate(user=self.user)
        return cast(
            Response,
            self.client.post(
                self.list_url,
                self.address_data(**overrides),
                format='json',
            ),
        )

    def create_address_for(self, user: Any, **overrides: Any) -> DeliveryAddress:
        data = self.address_data(**overrides)
        return DeliveryAddress.objects.create(
            user=user,
            label=data['label'],
            formatted_address=data['formatted_address'],
            street=data['street'],
            building=data['building'],
            apartment=data['apartment'],
            entrance=data['entrance'],
            floor=data['floor'],
            delivery_notes=data['delivery_notes'],
            contact_phone=data['contact_phone'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            is_default=overrides.pop('is_default', False),
        )

    def test_authenticated_user_can_create_address_and_first_is_default(self) -> None:
        response = self.create_address()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_default'])
        self.assertEqual(response.data['latitude'], '50.619000')
        self.assertEqual(response.data['longitude'], '26.250000')

        address = DeliveryAddress.objects.get()
        self.assertEqual(address.user, self.user)
        self.assertTrue(address.is_default)

    def test_unauthenticated_user_cannot_create_address(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.list_url,
                self.address_data(),
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(DeliveryAddress.objects.exists())

    def test_new_address_requires_checkout_fields(self) -> None:
        data = self.address_data()
        data.pop('street')
        data.pop('building')
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.post(self.list_url, data, format='json'),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('street', response.data)
        self.assertIn('building', response.data)
        self.assertFalse(DeliveryAddress.objects.exists())

    def test_setting_default_unsets_previous_default(self) -> None:
        first_response = self.create_address()
        second_response = self.create_address(
            label='Work',
            formatted_address='Rivne, Kyivska Street 45',
            street='Kyivska Street',
            building='45',
        )

        response = cast(
            Response,
            self.client.post(
                reverse('delivery-address-set-default', args=[second_response.data['id']]),
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_default'])
        self.assertEqual(
            DeliveryAddress.objects.filter(user=self.user, is_default=True).count(),
            1,
        )
        self.assertFalse(
            DeliveryAddress.objects.get(pk=first_response.data['id']).is_default
        )

    def test_deleting_default_promotes_remaining_address(self) -> None:
        first_response = self.create_address()
        second_response = self.create_address(
            label='Work',
            formatted_address='Rivne, Kyivska Street 45',
            street='Kyivska Street',
            building='45',
        )

        response = cast(
            Response,
            self.client.delete(
                reverse('delivery-address-detail', args=[first_response.data['id']]),
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(
            DeliveryAddress.objects.get(pk=second_response.data['id']).is_default
        )

    def test_default_address_endpoint_returns_current_default(self) -> None:
        created = self.create_address()

        response = cast(Response, self.client.get(self.default_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], created.data['id'])

    def test_address_rejects_invalid_latitude(self) -> None:
        response = self.create_address(latitude='90.000001')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latitude', response.data)

    def test_address_rejects_invalid_longitude(self) -> None:
        response = self.create_address(longitude='180.000001')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('longitude', response.data)

    def test_address_rejects_latitude_without_longitude(self) -> None:
        data = self.address_data()
        data.pop('longitude')
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.post(self.list_url, data, format='json'),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('longitude', response.data)

    def test_address_rejects_longitude_without_latitude(self) -> None:
        data = self.address_data()
        data.pop('latitude')
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.post(self.list_url, data, format='json'),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latitude', response.data)

    def test_user_cannot_read_another_users_address(self) -> None:
        other_address = self.create_address_for(self.other_user)
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.get(
                reverse('delivery-address-detail', args=[other_address.id]),
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_another_users_address(self) -> None:
        other_address = self.create_address_for(self.other_user)
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                reverse('delivery-address-detail', args=[other_address.id]),
                {'label': 'Changed'},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_address.refresh_from_db()
        self.assertEqual(other_address.label, 'Home')

    def test_user_cannot_delete_another_users_address(self) -> None:
        other_address = self.create_address_for(self.other_user)
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.delete(
                reverse('delivery-address-detail', args=[other_address.id]),
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(DeliveryAddress.objects.filter(pk=other_address.id).exists())

    def test_user_cannot_set_another_users_address_as_default(self) -> None:
        other_address = self.create_address_for(self.other_user)
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.post(
                reverse('delivery-address-set-default', args=[other_address.id]),
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(other_address.is_default)

    def test_profile_accepts_valid_avatar_and_allows_changes(self) -> None:
        self.client.force_authenticate(user=self.user)

        first_response = cast(
            Response,
            self.client.patch(
                self.profile_url,
                {'avatar': 'avatar_03'},
                format='json',
            ),
        )
        second_response = cast(
            Response,
            self.client.patch(
                self.profile_url,
                {'avatar': 'avatar_06'},
                format='json',
            ),
        )

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data['avatar'], 'avatar_06')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.avatar, 'avatar_06')

    def test_profile_rejects_invalid_avatar(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = cast(
            Response,
            self.client.patch(
                self.profile_url,
                {'avatar': 'not-an-avatar'},
                format='json',
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('avatar', response.data)

    def test_avatar_options_returns_controlled_avatar_ids(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = cast(Response, self.client.get(self.avatar_options_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatars'][0]['id'], 'avatar_01')
        self.assertEqual(len(response.data['avatars']), 6)


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
                password='CurrentPass123!', is_verified=True,
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
                password='CurrentPass123!', is_verified=True,
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
