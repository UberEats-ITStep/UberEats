import io
from decimal import Decimal
from typing import cast

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from .models import Category, Cuisine, MenuItem, Restaurant


def _valid_png_bytes() -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
    return buf.getvalue()


def make_cuisine(name="Japanese"):
    return Cuisine.objects.get_or_create(name=name)[0]


class RestaurantImageValidationTests(TestCase):
    def setUp(self):
        self.cuisine = make_cuisine()

    def test_valid_image_upload_passes_validation(self):
        restaurant = Restaurant(
            name="Valid Image Spot",
            cuisine=self.cuisine,
            image=SimpleUploadedFile("photo.png", _valid_png_bytes(), content_type="image/png"),
        )
        restaurant.full_clean()  # should not raise
        restaurant.save()
        self.assertTrue(restaurant.image.name.endswith(".png"))

    def test_rejects_unsupported_extension(self):
        restaurant = Restaurant(
            name="Bad Extension Spot",
            cuisine=self.cuisine,
            image=SimpleUploadedFile("notes.txt", b"just some text", content_type="text/plain"),
        )
        with self.assertRaises(ValidationError):
            restaurant.full_clean()

    def test_rejects_corrupted_image_bytes(self):
        restaurant = Restaurant(
            name="Corrupted Spot",
            cuisine=self.cuisine,
            image=SimpleUploadedFile("photo.png", b"not actually a png", content_type="image/png"),
        )
        with self.assertRaises(ValidationError):
            restaurant.full_clean()

    def test_rejects_oversized_image(self):
        oversized = b"0" * (6 * 1024 * 1024)  # 6MB > 5MB limit
        restaurant = Restaurant(
            name="Huge Image Spot",
            cuisine=self.cuisine,
            image=SimpleUploadedFile("photo.png", oversized, content_type="image/png"),
        )
        with self.assertRaises(ValidationError):
            restaurant.full_clean()

    def test_no_image_resolves_to_placeholder(self):
        restaurant = Restaurant.objects.create(name="No Image Spot", cuisine=self.cuisine)
        self.assertEqual(restaurant.resolved_image_url, "/static/images/placeholders/restaurant.png")

    def test_legacy_image_url_used_when_no_upload(self):
        restaurant = Restaurant.objects.create(
            name="Legacy URL Spot", cuisine=self.cuisine, image_url="https://example.com/a.jpg"
        )
        self.assertEqual(restaurant.resolved_image_url, "https://example.com/a.jpg")

    def test_uploaded_image_takes_priority_over_legacy_url(self):
        restaurant = Restaurant.objects.create(
            name="Both Set Spot",
            cuisine=self.cuisine,
            image_url="https://example.com/a.jpg",
            image=SimpleUploadedFile("photo.png", _valid_png_bytes(), content_type="image/png"),
        )
        self.assertNotEqual(restaurant.resolved_image_url, "https://example.com/a.jpg")
        self.assertIn("photo", restaurant.resolved_image_url)


class MenuItemImageValidationTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Item Spot", cuisine=make_cuisine())
        self.category = Category.objects.create(name="Mains")

    def test_rejects_unsupported_extension(self):
        item = MenuItem(
            restaurant=self.restaurant,
            category=self.category,
            name="Bad Photo Dish",
            price=Decimal("10.00"),
            image=SimpleUploadedFile("recipe.pdf", b"%PDF-1.4 fake", content_type="application/pdf"),
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_no_image_resolves_to_placeholder(self):
        item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Plain Dish", price=Decimal("10.00")
        )
        self.assertEqual(item.resolved_image_url, "/static/images/placeholders/menu_item.png")


class SerializerImageResolutionTests(APITestCase):
    def setUp(self):
        self.cuisine = make_cuisine()

    def test_restaurant_list_returns_placeholder_when_no_image(self):
        Restaurant.objects.create(name="Placeholder Spot", cuisine=self.cuisine)

        response = cast(Response, self.client.get(reverse("restaurant-list")))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data[0]["image_url"].endswith("/placeholders/restaurant.png"))

    def test_restaurant_list_returns_legacy_image_url_unchanged(self):
        Restaurant.objects.create(
            name="Legacy Spot", cuisine=self.cuisine, image_url="https://example.com/x.jpg"
        )

        response = cast(Response, self.client.get(reverse("restaurant-list")))

        self.assertEqual(response.data[0]["image_url"], "https://example.com/x.jpg")

    def test_menu_item_image_never_empty_string(self):
        restaurant = Restaurant.objects.create(name="Menu Img Spot", cuisine=self.cuisine)
        category = Category.objects.create(name="Mains")
        MenuItem.objects.create(
            restaurant=restaurant, category=category, name="No Photo Dish", price=Decimal("5.00")
        )

        response = cast(Response, self.client.get(reverse("restaurant-detail", args=[restaurant.id])))

        image_value = response.data["categories"][0]["menu_items"][0]["image"]
        self.assertNotEqual(image_value, "")
        self.assertIsNotNone(image_value)


class SeedMediaCommandTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command("seed_media")
        first_restaurant_count = Restaurant.objects.count()
        first_item_count = MenuItem.objects.count()

        call_command("seed_media")

        self.assertEqual(Restaurant.objects.count(), first_restaurant_count)
        self.assertEqual(MenuItem.objects.count(), first_item_count)

    def test_seed_assigns_non_empty_image_urls(self):
        call_command("seed_media")

        for restaurant in Restaurant.objects.all():
            self.assertTrue(restaurant.image_url)
            self.assertTrue(restaurant.image_url.startswith("https://"))

        for item in MenuItem.objects.all():
            self.assertTrue(item.image_url)
            self.assertTrue(item.image_url.startswith("https://"))