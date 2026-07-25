from django.test import TestCase

# Create your tests here.
from typing import Any, cast

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase

from restaurants.models import Category, Cuisine, MenuItem, Restaurant
from .models import Cart, CartItem


UserModel: Any = get_user_model()


class CartModelTests(TestCase):

    def setUp(self) -> None:
        self.user = cast(
            Any,
            UserModel.objects.create_user(
                username="john",
                email="john@example.com",
                password="TestPass123!",
            )
        )

        self.cuisine = Cuisine.objects.create(name='American')
        self.restaurant = Restaurant.objects.create(name="McDonalds", cuisine=self.cuisine)
        self.category = Category.objects.create(name="Burgers")

        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Big Mac",
            price=120,
        )

    def test_cart_creation(self) -> None:
        cart = Cart.objects.create(user=self.user)

        self.assertEqual(cart.user, self.user)

    def test_cart_item_creation(self) -> None:
        cart = Cart.objects.create(user=self.user)

        item = CartItem.objects.create(
            cart=cart,
            menu_item=self.menu_item,
            quantity=2,
        )

        self.assertEqual(item.cart, cart)
        self.assertEqual(item.menu_item, self.menu_item)
        self.assertEqual(item.quantity, 2)

    def test_cart_has_items(self) -> None:
        cart = Cart.objects.create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            menu_item=self.menu_item,
            quantity=1,
        )

        self.assertEqual(cart.items.count(), 1)


class CartApiTests(APITestCase):

    def setUp(self) -> None:
        self.user = cast(
            Any,
            UserModel.objects.create_user(
                username="john",
                email="john@example.com",
                password="TestPass123!",
            )
        )

        self.client.force_authenticate(self.user)

        self.cart = Cart.objects.create(user=self.user)

        self.cuisine = Cuisine.objects.create(name='Fast Food')
        self.restaurant1 = Restaurant.objects.create(name="McDonalds", cuisine=self.cuisine)
        self.restaurant2 = Restaurant.objects.create(name="KFC", cuisine=self.cuisine)

        self.category1 = Category.objects.create(
            name="Burgers1",
        )

        self.category2 = Category.objects.create(
            name="Chicken",
        )

        self.burger = MenuItem.objects.create(
            restaurant=self.restaurant1,
            category=self.category1,
            name="Big Mac",
            price=120,
        )

        self.bucket = MenuItem.objects.create(
            restaurant=self.restaurant2,
            category=self.category2,
            name="Bucket",
            price=300,
        )

        self.url = reverse("cartitem-list")

    def test_add_item_to_cart(self) -> None:
        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    "cart": self.cart.id,
                    "menu_item": self.burger.id,
                    "quantity": 2,
                },
                format="json",
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_cart_accepts_only_one_restaurant(self) -> None:
        self.cart.restaurant = self.restaurant1
        self.cart.save()
        CartItem.objects.create(
            cart=self.cart,
            menu_item=self.burger,
            quantity=1,
        )

        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    "cart": self.cart.id,
                    "menu_item": self.bucket.id,
                    "quantity": 1,
                },
                format="json",
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_add_second_item_from_same_restaurant(self) -> None:
        fries = MenuItem.objects.create(
            restaurant=self.restaurant1,
            category=self.category1,
            name="Fries",
            price=70,
        )

        self.cart.restaurant = self.restaurant1
        self.cart.save()
        CartItem.objects.create(
            cart=self.cart,
            menu_item=self.burger,
            quantity=1,
        )

        response = cast(
            Response,
            self.client.post(
                self.url,
                {
                    "cart": self.cart.id,
                    "menu_item": fries.id,
                    "quantity": 2,
                },
                format="json",
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.cart.items.count(), 2)

    def test_get_cart(self) -> None:
        url = reverse("cart-detail", args=[self.cart.id])

        response = cast(Response, self.client.get(url))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self) -> None:
        self.client.force_authenticate(user=None)
        response = cast(Response, self.client.get(self.url))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_access(self) -> None:
        user2 = UserModel.objects.create_user(username="jane", email="jane@example.com", password="pwd")
        self.client.force_authenticate(user2)
        url = reverse("cart-detail", args=[self.cart.id])
        response = cast(Response, self.client.get(url))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_quantity(self) -> None:
        item = CartItem.objects.create(cart=self.cart, menu_item=self.burger, quantity=1)
        url = reverse("cartitem-detail", args=[item.id])
        response = cast(Response, self.client.patch(url, {"quantity": 5}, format="json"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_duplicate_item_increases_quantity(self) -> None:
        self.cart.restaurant = self.restaurant1
        self.cart.save()
        CartItem.objects.create(cart=self.cart, menu_item=self.burger, quantity=1)
        response = cast(Response, self.client.post(self.url, {
            "cart": self.cart.id,
            "menu_item": self.burger.id,
            "quantity": 2
        }, format="json"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.items.first().quantity, 3)