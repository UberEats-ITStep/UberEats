from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.services.firebase_auth import (
    FirebaseAuthenticationError,
    FirebaseIdentity,
)


class FirebaseLoginTests(APITestCase):
    def firebase_login(self, identity):
        with patch("users.views.verify_firebase_id_token", return_value=identity):
            return self.client.post(
                reverse("firebase-login"),
                {"id_token": "verified-firebase-token"},
                format="json",
            )

    def test_missing_token_is_rejected(self):
        response = self.client.post(reverse("firebase-login"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "A Firebase ID token is required.")

    def test_invalid_or_expired_token_is_rejected(self):
        with patch(
            "users.views.verify_firebase_id_token",
            side_effect=FirebaseAuthenticationError(
                "The Firebase ID token is invalid or expired."
            ),
        ):
            response = self.client.post(
                reverse("firebase-login"),
                {"id_token": "expired-token"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_firebase_identity_creates_verified_django_user(self):
        response = self.firebase_login(FirebaseIdentity(
            uid="firebase-new-user",
            email="new@example.com",
            given_name="New",
            family_name="Person",
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.firebase_uid, "firebase-new-user")
        self.assertTrue(user.is_verified)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.first_name, "New")

    def test_existing_user_is_linked_without_replacing_profile_data(self):
        user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="ExistingPass123!",
        )
        user.profile.phone_number = "+380501234567"
        user.profile.save(update_fields=["phone_number"])

        response = self.firebase_login(FirebaseIdentity(
            uid="firebase-existing-user",
            email="EXISTING@example.com",
        ))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.firebase_uid, "firebase-existing-user")
        self.assertTrue(user.has_usable_password())
        self.assertEqual(user.profile.phone_number, "+380501234567")

    def test_firebase_uid_with_different_email_is_rejected(self):
        User.objects.create_user(
            username="linked",
            email="first@example.com",
            password="ExistingPass123!",
            firebase_uid="already-linked-uid",
        )

        response = self.firebase_login(FirebaseIdentity(
            uid="already-linked-uid",
            email="other@example.com",
        ))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(User.objects.filter(email="other@example.com").exists())

    def test_returned_django_token_authenticates_existing_protected_api(self):
        response = self.firebase_login(FirebaseIdentity(
            uid="firebase-protected-user",
            email="protected@example.com",
        ))
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

        profile_response = self.client.get(reverse("profile"))

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["email"], "protected@example.com")
