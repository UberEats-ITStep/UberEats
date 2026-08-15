from typing import Any, cast

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from .models import Profile


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
