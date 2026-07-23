from decimal import Decimal
from typing import cast

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from .models import Category, Cuisine, MenuItem, Restaurant
from .serializers import RestaurantDetailSerializer


def create_restaurant(*, name: str = "Sushi Place") -> Restaurant:
    cuisine, _ = Cuisine.objects.get_or_create(name="Japanese")
    return Restaurant.objects.create(
        name=name,
        description="Fresh sushi and rolls.",
        image_url="https://example.com/sushi.jpg",
        address="Kyiv",
        latitude=Decimal("50.450100"),
        longitude=Decimal("30.523400"),
        cuisine=cuisine,
        rating=Decimal("4.70"),
        delivery_time=35,
    )


class RestaurantModelTests(TestCase):
    def test_restaurant_menuitem_relationships_work_with_global_categories(self):
        restaurant = create_restaurant()
        category = Category.objects.create(name="Rolls")
        menu_item = MenuItem.objects.create(
            restaurant=restaurant,
            category=category,
            name="Salmon Roll",
            description="Fresh salmon roll.",
            price=Decimal("12.50"),
            image_url="https://example.com/salmon-roll.jpg",
            is_available=True,
        )

        self.assertEqual(restaurant.menu_items.count(), 1)
        self.assertEqual(category.menu_items.count(), 1)
        self.assertEqual(menu_item.restaurant, restaurant)
        self.assertEqual(menu_item.category, category)
        self.assertEqual(menu_item.price, Decimal("12.50"))


class RestaurantSerializerTests(TestCase):
    def test_detail_serializer_groups_menu_items_by_category(self):
        restaurant = create_restaurant()
        rolls = Category.objects.create(name="Rolls")
        drinks = Category.objects.create(name="Drinks")
        menu_item = MenuItem.objects.create(
            restaurant=restaurant,
            category=rolls,
            name="Salmon Roll",
            description="Fresh salmon roll.",
            price=Decimal("12.50"),
            image_url="https://example.com/salmon-roll.jpg",
            is_available=True,
        )

        data = RestaurantDetailSerializer(instance=restaurant).data

        self.assertEqual(data["id"], restaurant.id)
        self.assertEqual(data["cuisine_name"], "Japanese")
        self.assertEqual(
            data["categories"],
            [
                {
                    "id": rolls.id,
                    "name": "Rolls",
                    "menu_items": [
                        {
                            "id": menu_item.id,
                            "category": rolls.id,
                            "category_name": "Rolls",
                            "name": "Salmon Roll",
                            "description": "Fresh salmon roll.",
                            "price": "12.50",
                            "image_url": "https://example.com/salmon-roll.jpg",
                            "is_available": True,
                        }
                    ],
                }
            ],
        )
        self.assertNotIn(drinks.id, [category["id"] for category in data["categories"]])


class RestaurantApiTests(APITestCase):
    def setUp(self) -> None:
        self.list_url = reverse("restaurant-list")

    def create_restaurant_graph(self):
        restaurant = create_restaurant()
        rolls = Category.objects.create(name="Rolls")
        drinks = Category.objects.create(name="Drinks")
        MenuItem.objects.create(
            restaurant=restaurant,
            category=rolls,
            name="Salmon Roll",
            description="Fresh salmon roll.",
            price=Decimal("12.50"),
            image_url="https://example.com/salmon-roll.jpg",
            is_available=True,
        )
        MenuItem.objects.create(
            restaurant=restaurant,
            category=drinks,
            name="Green Tea",
            description="Hot green tea.",
            price=Decimal("3.50"),
            image_url="https://example.com/green-tea.jpg",
            is_available=False,
        )
        return restaurant, rolls, drinks

    def test_restaurant_list_returns_schema_fields(self):
        sushi = create_restaurant(name="Sushi Place")
        burger = create_restaurant(name="Burger Place")

        response = cast(Response, self.client.get(self.list_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "id": sushi.id,
                    "name": "Sushi Place",
                    "description": "Fresh sushi and rolls.",
                    "image_url": "https://example.com/sushi.jpg",
                    "address": "Kyiv",
                    "latitude": "50.450100",
                    "longitude": "30.523400",
                    "cuisine": sushi.cuisine_id,
                    "cuisine_name": "Japanese",
                    "rating": "4.70",
                    "review_count": 0,
                    "delivery_time": 35,
                },
                {
                    "id": burger.id,
                    "name": "Burger Place",
                    "description": "Fresh sushi and rolls.",
                    "image_url": "https://example.com/sushi.jpg",
                    "address": "Kyiv",
                    "latitude": "50.450100",
                    "longitude": "30.523400",
                    "cuisine": burger.cuisine_id,
                    "cuisine_name": "Japanese",
                    "rating": "4.70",
                    "review_count": 0,
                    "delivery_time": 35,
                },
            ],
        )

    def test_restaurant_detail_returns_grouped_categories_and_menu_items(self):
        restaurant, rolls, drinks = self.create_restaurant_graph()
        url = reverse("restaurant-detail", args=[restaurant.id])

        with self.assertNumQueries(2):
            response = cast(Response, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], restaurant.id)
        self.assertEqual(response.data["name"], "Sushi Place")
        self.assertEqual(response.data["cuisine_name"], "Japanese")
        self.assertEqual(len(response.data["categories"]), 2)
        self.assertEqual(response.data["categories"][0]["id"], rolls.id)
        self.assertEqual(response.data["categories"][0]["menu_items"][0]["name"], "Salmon Roll")
        self.assertEqual(response.data["categories"][1]["id"], drinks.id)
        self.assertEqual(response.data["categories"][1]["menu_items"][0]["is_available"], False)

    def test_restaurant_detail_returns_404_for_invalid_id(self):
        url = reverse("restaurant-detail", args=[999999])

        response = cast(Response, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_restaurant_detail_handles_restaurant_without_menu_items(self):
        restaurant = create_restaurant(name="Solo Kitchen")
        url = reverse("restaurant-detail", args=[restaurant.id])

        response = cast(Response, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": restaurant.id,
                "name": "Solo Kitchen",
                "description": "Fresh sushi and rolls.",
                "image_url": "https://example.com/sushi.jpg",
                "address": "Kyiv",
                "latitude": "50.450100",
                "longitude": "30.523400",
                "cuisine": restaurant.cuisine_id,
                "cuisine_name": "Japanese",
                "rating": "4.70",
                "review_count": 0,
                "delivery_time": 35,
                "categories": [],
            },
        )

    def test_restaurant_list_uses_single_query(self):
        create_restaurant(name="Sushi Place")
        create_restaurant(name="Burger Place")

        with self.assertNumQueries(1):
            response = cast(Response, self.client.get(self.list_url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
