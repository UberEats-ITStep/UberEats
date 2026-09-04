from datetime import datetime, time
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from .models import Category, Cuisine, MenuItem, OpeningHours, Restaurant
from .serializers import MenuItemSerializer


def create_restaurant(*, name="Sushi Place", **overrides):
    cuisine, _ = Cuisine.objects.get_or_create(name="Japanese")
    values = {
        "name": name,
        "description": "Fresh sushi and rolls.",
        "image_url": "https://example.com/sushi.jpg",
        "address": "Kyiv",
        "latitude": Decimal("50.450100"),
        "longitude": Decimal("30.523400"),
        "cuisine": cuisine,
        "rating": Decimal("4.70"),
        "delivery_time": 35,
    }
    values.update(overrides)
    return Restaurant.objects.create(**values)


class RestaurantValidationTests(TestCase):
    def test_coordinates_must_be_supplied_together(self):
        restaurant = create_restaurant(longitude=None)

        with self.assertRaises(ValidationError) as error:
            restaurant.full_clean()

        self.assertIn("longitude", error.exception.message_dict)

    def test_coordinate_ranges_rating_and_delivery_time_are_validated(self):
        restaurant = create_restaurant(
            latitude=Decimal("91"),
            longitude=Decimal("181"),
            rating=Decimal("5.01"),
            delivery_time=0,
        )

        with self.assertRaises(ValidationError) as error:
            restaurant.full_clean()

        self.assertEqual(
            set(error.exception.message_dict),
            {"latitude", "longitude", "rating", "delivery_time"},
        )


class OpeningHoursTests(TestCase):
    def setUp(self):
        self.restaurant = create_restaurant()

    def test_opening_and_closing_times_must_differ(self):
        hours = OpeningHours(
            restaurant=self.restaurant,
            opens_at=time(9),
            closes_at=time(9),
        )

        with self.assertRaises(ValidationError) as error:
            hours.full_clean()

        self.assertIn("closes_at", error.exception.message_dict)

    def test_only_one_schedule_per_day_type_is_allowed(self):
        OpeningHours.objects.create(
            restaurant=self.restaurant,
            day_type="weekday",
            opens_at=time(9),
            closes_at=time(17),
        )

        with self.assertRaises(ValidationError):
            OpeningHours(
                restaurant=self.restaurant,
                day_type="weekday",
                opens_at=time(10),
                closes_at=time(18),
            ).full_clean()

    def test_weekday_and_weekend_schedules_are_used(self):
        OpeningHours.objects.create(
            restaurant=self.restaurant,
            day_type="weekday",
            opens_at=time(9),
            closes_at=time(17),
        )
        OpeningHours.objects.create(
            restaurant=self.restaurant,
            day_type="weekend",
            opens_at=time(11),
            closes_at=time(15),
        )

        with patch("restaurants.models.timezone.now", return_value=self.aware(2026, 7, 30, 12)):
            self.assertTrue(self.restaurant.is_open_now)
        with patch("restaurants.models.timezone.now", return_value=self.aware(2026, 8, 1, 10)):
            self.assertFalse(self.restaurant.is_open_now)

    def test_missing_schedule_is_closed(self):
        with patch("restaurants.models.timezone.now", return_value=self.aware(2026, 7, 30, 12)):
            self.assertFalse(self.restaurant.is_open_now)

    def test_overnight_schedule_includes_the_following_day(self):
        OpeningHours.objects.create(
            restaurant=self.restaurant,
            day_type="weekend",
            opens_at=time(18),
            closes_at=time(2),
        )

        with patch("restaurants.models.timezone.now", return_value=self.aware(2026, 8, 2, 23)):
            self.assertTrue(self.restaurant.is_open_now)
        with patch("restaurants.models.timezone.now", return_value=self.aware(2026, 8, 3, 1)):
            self.assertTrue(self.restaurant.is_open_now)
        with patch("restaurants.models.timezone.now", return_value=self.aware(2026, 8, 3, 3)):
            self.assertFalse(self.restaurant.is_open_now)

    @staticmethod
    def aware(year, month, day, hour):
        return timezone.make_aware(datetime(year, month, day, hour))


class MenuItemTests(TestCase):
    def setUp(self):
        self.restaurant = create_restaurant()
        self.category = Category.objects.create(name="Rolls")

    def make_item(self, **overrides):
        values = {
            "restaurant": self.restaurant,
            "category": self.category,
            "name": "Salmon Roll",
            "price": Decimal("12.50"),
        }
        values.update(overrides)
        return MenuItem(**values)

    def test_price_must_be_greater_than_zero(self):
        with self.assertRaises(ValidationError) as error:
            self.make_item(price=0).full_clean()
        self.assertIn("price", error.exception.message_dict)

    def test_availability_and_reason_must_be_consistent(self):
        for item in (
            self.make_item(is_available=True, unavailable_reason="Sold out"),
            self.make_item(is_available=False, unavailable_reason=""),
        ):
            with self.assertRaises(ValidationError) as error:
                item.full_clean()
            self.assertIn("unavailable_reason", error.exception.message_dict)

    def test_duplicate_names_get_unique_restaurant_slugs(self):
        first = self.make_item()
        first.save()
        second = self.make_item()
        second.save()

        self.assertEqual(first.slug, "salmon-roll")
        self.assertEqual(second.slug, "salmon-roll-2")

    def test_same_slug_can_be_used_by_different_restaurants(self):
        first = self.make_item()
        first.save()
        other = create_restaurant(name="Other")
        second = self.make_item(restaurant=other)
        second.save()

        self.assertEqual(first.slug, second.slug)

    @override_settings(MEDIA_URL="/media/")
    def test_images_return_url_or_null(self):
        request = APIRequestFactory().get("/")
        empty = self.make_item()
        image = self.make_item(
            name="Tuna Roll",
            image=SimpleUploadedFile("tuna.jpg", b"image", content_type="image/jpeg"),
        )

        self.assertTrue(
            MenuItemSerializer(empty, context={"request": request})
            .data["image_url"]
            .endswith("/static/images/placeholders/menu_item.png")
        )
        self.assertTrue(
            MenuItemSerializer(image, context={"request": request})
            .data["image_url"]
            .startswith("http://testserver/media/")
        )


class RestaurantApiTests(APITestCase):
    def setUp(self):
        self.list_url = reverse("restaurant-list")

    def create_graph(self):
        restaurant = create_restaurant()
        OpeningHours.objects.create(
            restaurant=restaurant,
            day_type="weekday",
            opens_at=time(9),
            closes_at=time(22),
        )
        category = Category.objects.create(name="Rolls")
        available = MenuItem.objects.create(
            restaurant=restaurant,
            category=category,
            name="Salmon Roll",
            description="Fresh salmon roll.",
            price=Decimal("12.50"),
            is_available=True,
            is_vegetarian=False,
            is_vegan=False,
            calories=320,
        )
        unavailable = MenuItem.objects.create(
            restaurant=restaurant,
            category=category,
            name="Tuna Roll",
            price=Decimal("13.50"),
            is_available=False,
            unavailable_reason="Sold out",
        )
        return restaurant, category, available, unavailable

    def test_list_shape_remains_unpaginated_and_query_efficient(self):
        create_restaurant(name="Sushi Place")
        create_restaurant(name="Burger Place")

        with self.assertNumQueries(2):
            response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 2)
        self.assertIn("is_open_now", response.data[0])

    def test_detail_contains_complete_schedule_and_menu_metadata(self):
        restaurant, category, available, unavailable = self.create_graph()

        with self.assertNumQueries(4):
            response = self.client.get(reverse("restaurant-detail", args=[restaurant.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["opening_hours"][0]["day_type"], "weekday")
        self.assertEqual(response.data["categories"][0]["id"], category.pk)
        items = response.data["categories"][0]["menu_items"]
        self.assertEqual([item["id"] for item in items], [available.pk, unavailable.pk])
        self.assertEqual(items[0]["slug"], "salmon-roll")
        self.assertEqual(items[0]["calories"], 320)
        self.assertEqual(items[0]["image"], items[0]["image_url"])
        self.assertTrue(items[0]["image_url"].endswith("/static/images/placeholders/menu_item.png"))
        self.assertFalse(items[1]["is_available"])
        self.assertEqual(items[1]["unavailable_reason"], "Sold out")

    def test_detail_without_hours_or_items_is_compatible(self):
        restaurant = create_restaurant(name="Solo Kitchen")
        response = self.client.get(reverse("restaurant-detail", args=[restaurant.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_open_now"])
        self.assertEqual(response.data["opening_hours"], [])
        self.assertEqual(response.data["categories"], [])

    def test_search_matches_restaurant_cuisine_and_menu_item(self):
        sushi = create_restaurant(name="Sakura", description="Traditional Japanese food")
        burger_cuisine = Cuisine.objects.create(name="American")
        burger = create_restaurant(
            name="Downtown Grill",
            description="Charcoal classics",
            cuisine=burger_cuisine,
        )
        category = Category.objects.create(name="Mains")
        MenuItem.objects.create(
            restaurant=burger,
            category=category,
            name="Truffle Burger",
            price=Decimal("15.00"),
        )

        for query, expected in (
            ("Sakura", sushi),
            ("Japanese", sushi),
            ("Truffle", burger),
        ):
            with self.subTest(query=query):
                response = self.client.get(self.list_url, {"search": query})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual([item["id"] for item in response.data], [expected.pk])

    def test_filters_by_cuisine_and_minimum_rating(self):
        japanese = Cuisine.objects.get_or_create(name="Japanese")[0]
        american = Cuisine.objects.create(name="American")
        matching = create_restaurant(
            name="Top Sushi",
            cuisine=japanese,
            rating=Decimal("4.80"),
        )
        create_restaurant(name="Low Sushi", cuisine=japanese, rating=Decimal("3.20"))
        create_restaurant(name="Top Burger", cuisine=american, rating=Decimal("4.90"))

        response = self.client.get(
            self.list_url,
            {"cuisine": japanese.pk, "rating__gte": "4.0"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [matching.pk])

    def test_orders_restaurants_by_supported_fields(self):
        create_restaurant(name="Slower", rating=Decimal("4.80"), delivery_time=50)
        faster = create_restaurant(name="Faster", rating=Decimal("4.10"), delivery_time=20)

        fastest_response = self.client.get(self.list_url, {"ordering": "delivery_time"})
        rating_response = self.client.get(self.list_url, {"ordering": "-rating"})

        self.assertEqual(fastest_response.data[0]["id"], faster.pk)
        self.assertEqual(rating_response.data[0]["name"], "Slower")


class SeedAndMigrationTests(TestCase):
    def test_seed_db_is_idempotent_and_complete(self):
        output = StringIO()
        call_command("seed_db", stdout=output)
        counts = (
            Restaurant.objects.count(),
            OpeningHours.objects.count(),
            MenuItem.objects.count(),
        )
        call_command("seed_db", stdout=output)

        self.assertEqual(
            counts,
            (
                Restaurant.objects.count(),
                OpeningHours.objects.count(),
                MenuItem.objects.count(),
            ),
        )
        self.assertEqual(OpeningHours.objects.count(), Restaurant.objects.count() * 2)
        self.assertTrue(MenuItem.objects.filter(is_available=True).exists())
        self.assertTrue(MenuItem.objects.filter(is_available=False).exists())
        self.assertTrue(MenuItem.objects.filter(calories__isnull=False).exists())
        self.assertFalse(Restaurant.objects.filter(image_url__contains="example.com").exists())
        self.assertFalse(MenuItem.objects.filter(image_url="").exists())

    def test_test_database_has_all_migration_leaf_nodes_applied(self):
        executor = MigrationExecutor(connection)
        applied = set(executor.loader.applied_migrations)
        self.assertTrue(set(executor.loader.graph.leaf_nodes()).issubset(applied))
