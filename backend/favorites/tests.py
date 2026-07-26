from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import Cuisine, Restaurant

from .models import Favorite


User = get_user_model()


def create_user(email: str):
    return User.objects.create_user(
        email=email,
        username=email.split("@")[0],
        password="TestPass123!",
    )


def create_restaurant(name: str) -> Restaurant:
    cuisine, _ = Cuisine.objects.get_or_create(name="Italian")
    return Restaurant.objects.create(
        name=name,
        cuisine=cuisine,
        description="A neighborhood restaurant.",
        image_url="https://example.com/restaurant.jpg",
        rating=Decimal("4.50"),
        delivery_time=30,
    )


class FavoriteModelTests(TestCase):
    def setUp(self):
        self.user = create_user("client@example.com")
        self.restaurant = create_restaurant("Pizza Place")

    def test_favorite_relationships_and_default_ordering(self):
        favorite = Favorite.objects.create(
            user=self.user,
            restaurant=self.restaurant,
        )

        self.assertEqual(self.user.favorites.get(), favorite)
        self.assertEqual(self.restaurant.favorites.get(), favorite)
        self.assertIsNotNone(favorite.created_at)

    def test_database_constraint_prevents_duplicates(self):
        Favorite.objects.create(user=self.user, restaurant=self.restaurant)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=self.user, restaurant=self.restaurant)

    def test_deleting_user_or_restaurant_cascades_favorites(self):
        Favorite.objects.create(user=self.user, restaurant=self.restaurant)
        self.user.delete()
        self.assertFalse(Favorite.objects.exists())

        second_user = create_user("second@example.com")
        second_restaurant = create_restaurant("Pasta Place")
        Favorite.objects.create(user=second_user, restaurant=second_restaurant)
        second_restaurant.delete()
        self.assertFalse(Favorite.objects.exists())


class FavoriteApiTests(APITestCase):
    def setUp(self):
        self.user = create_user("client@example.com")
        self.other_user = create_user("other@example.com")
        self.restaurant = create_restaurant("Pizza Place")
        self.other_restaurant = create_restaurant("Pasta Place")
        self.list_url = reverse("favorite-list")

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def test_authentication_is_required(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_favorite_returns_restaurant_details(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {"restaurant": self.restaurant.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["restaurant"], self.restaurant.id)
        self.assertEqual(
            response.data["restaurant_detail"]["name"],
            self.restaurant.name,
        )
        self.assertTrue(
            Favorite.objects.filter(
                user=self.user,
                restaurant=self.restaurant,
            ).exists()
        )

    def test_duplicate_favorite_returns_clear_validation_error(self):
        self.authenticate()
        Favorite.objects.create(user=self.user, restaurant=self.restaurant)

        response = self.client.post(
            self.list_url,
            {"restaurant": self.restaurant.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already in your favorites", str(response.data))
        self.assertEqual(Favorite.objects.count(), 1)

    def test_invalid_restaurant_returns_validation_error(self):
        self.authenticate()

        response = self.client.post(
            self.list_url,
            {"restaurant": 999999},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_contains_only_authenticated_users_favorites(self):
        Favorite.objects.create(user=self.user, restaurant=self.restaurant)
        Favorite.objects.create(
            user=self.other_user,
            restaurant=self.other_restaurant,
        )
        self.authenticate()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["restaurant"], self.restaurant.id)

    def test_user_can_delete_own_favorite(self):
        favorite = Favorite.objects.create(
            user=self.user,
            restaurant=self.restaurant,
        )
        self.authenticate()

        response = self.client.delete(
            reverse("favorite-detail", args=[favorite.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.exists())

    def test_user_cannot_access_or_delete_another_users_favorite(self):
        favorite = Favorite.objects.create(
            user=self.other_user,
            restaurant=self.restaurant,
        )
        self.authenticate()
        detail_url = reverse("favorite-detail", args=[favorite.id])

        self.assertEqual(
            self.client.get(detail_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )
        self.assertEqual(
            self.client.delete(detail_url).status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertTrue(Favorite.objects.filter(pk=favorite.id).exists())

    def test_check_reports_favorite_status(self):
        Favorite.objects.create(user=self.user, restaurant=self.restaurant)
        self.authenticate()
        check_url = reverse("favorite-check")

        favorite_response = self.client.get(
            check_url,
            {"restaurant": self.restaurant.id},
        )
        other_response = self.client.get(
            check_url,
            {"restaurant": self.other_restaurant.id},
        )

        self.assertEqual(favorite_response.status_code, status.HTTP_200_OK)
        self.assertTrue(favorite_response.data["is_favorite"])
        self.assertFalse(other_response.data["is_favorite"])

    def test_check_validates_restaurant_parameter(self):
        self.authenticate()
        check_url = reverse("favorite-check")

        self.assertEqual(
            self.client.get(check_url).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self.client.get(check_url, {"restaurant": "invalid"}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            self.client.get(check_url, {"restaurant": 999999}).status_code,
            status.HTTP_404_NOT_FOUND,
        )
