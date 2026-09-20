"""
Regression tests for the access-control policy (see docs/permissions.md).

Route names come from your users/orders/payments/cart/favorites/reviews urls.py.
Run:  python manage.py test config.test_access_control
"""

import hashlib
import hmac
import json
import time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from favorites.models import Favorite
from orders.models import Order
from restaurants.models import Category, Cuisine, MenuItem, Restaurant
from reviews.models import Review
from users.models import DeliveryAddress
from users.permissions import is_admin

User = get_user_model()

URL = {
    # --- restaurants router (config/urls.py + restaurants/urls.py) ---
    "restaurant_list": "restaurant-list",
    "category_list": "category-list",
    "category_detail": "category-detail",
    "cuisine_list": "cuisine-list",
    "cuisine_detail": "cuisine-detail",
    "menuitem_list": "menuitem-list",
    "menuitem_detail": "menuitem-detail",
    # --- orders/urls.py ---
    "order_history": "order_history",
    "order_detail": "order_detail",
    "order_status": "order_status",
    # --- payments/urls.py ---
    "payment_intent": "create-intent",
    "webhook": "webhook",
    # --- users/urls.py ---
    "register": "register",
    "login": "login",
    "verify_email": "verify-email",
    "resend_verification": "resend-verification",
    "forgot_password": "forgot-password",
    "reset_password": "reset-password",
    "token_refresh": "token_refresh",
    "address_list": "delivery-address-list",
    "address_default": "delivery-address-default",
    "address_detail": "delivery-address-detail",
    "address_set_default": "delivery-address-set-default",
    # --- router basenames from cart/, favorites/, reviews/ urls.py ---
    "cartitem_list": "cartitem-list",
    "cartitem_detail": "cartitem-detail",
    "favorite_list": "favorite-list",
    "favorite_detail": "favorite-detail",
    "favorite_check": "favorite-check",
    "review_list": "review-list",
    "review_detail": "review-detail",
}


# Factories (Restaurant.cuisine is a required FK; Category/Cuisine names are unique).
def make_user(email, *, role="CLIENT", is_staff=False, password="Str0ng-pass!123"):
    return User.objects.create_user(
        username=email.split("@")[0],
        email=email,
        password=password,
        role=role,
        is_staff=is_staff,
        is_verified=True,
    )


def make_restaurant(name="Test Restaurant"):
    cuisine, _ = Cuisine.objects.get_or_create(name="Test cuisine")
    return Restaurant.objects.create(name=name, cuisine=cuisine, is_active=True)


def make_menu_item(restaurant, name="Burger"):
    category, _ = Category.objects.get_or_create(name="Mains")
    return MenuItem.objects.create(
        restaurant=restaurant, category=category, name=name,
        price=Decimal("10.00"), is_available=True,
    )


def make_order(client, restaurant, status=Order.STATUS_PENDING):
    return Order.objects.create(
        client=client, restaurant=restaurant, street="Some st", building="1", status=status,
    )


def rows(response):
    """List endpoints may or may not be paginated."""
    data = response.data
    return data["results"] if isinstance(data, dict) and "results" in data else data


CATALOG_ROUTES = ("category", "cuisine", "menuitem")


class CatalogPermissionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = make_user("customer@example.com")
        cls.admin_by_role = make_user("admin-role@example.com", role="ADMIN")
        cls.admin_by_staff = make_user("admin-staff@example.com", is_staff=True)

    def test_anonymous_can_read_public_catalog(self):
        for route in ("restaurant",) + CATALOG_ROUTES:
            with self.subTest(route=route):
                response = self.client.get(reverse(URL[f"{route}_list"]))
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _write_requests(self, route):
        detail = reverse(URL[f"{route}_detail"], kwargs={"pk": 999999})
        return (
            ("post", reverse(URL[f"{route}_list"])),
            ("put", detail), ("patch", detail), ("delete", detail),
        )

    def test_anonymous_cannot_write_catalog(self):
        for route in CATALOG_ROUTES:
            for method, url in self._write_requests(route):
                with self.subTest(route=route, method=method):
                    response = getattr(self.client, method)(url, {}, format="json")
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_write_catalog(self):
        self.client.force_authenticate(self.customer)
        for route in CATALOG_ROUTES:
            for method, url in self._write_requests(route):
                with self.subTest(route=route, method=method):
                    response = getattr(self.client, method)(url, {}, format="json")
                    self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_write_does_not_change_data(self):
        category = Category.objects.create(name="Keep me")
        self.client.force_authenticate(self.customer)
        self.client.patch(reverse(URL["category_detail"], kwargs={"pk": category.pk}),
                          {"name": "Hacked"}, format="json")
        self.client.delete(reverse(URL["category_detail"], kwargs={"pk": category.pk}))
        category.refresh_from_db()
        self.assertEqual(category.name, "Keep me")

    def test_admin_can_manage_catalog(self):
        for admin in (self.admin_by_role, self.admin_by_staff):
            self.client.force_authenticate(admin)
            for route in ("category", "cuisine"):
                with self.subTest(admin=admin.email, route=route):
                    created = self.client.post(reverse(URL[f"{route}_list"]),
                                               {"name": f"{route}-by-{admin.pk}"}, format="json")
                    self.assertEqual(created.status_code, status.HTTP_201_CREATED, created.data)
                    detail = reverse(URL[f"{route}_detail"], kwargs={"pk": created.data["id"]})
                    self.assertEqual(self.client.patch(detail, {"name": "renamed"}, format="json").status_code,
                                     status.HTTP_200_OK)
                    self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)

    def test_auth_errors_have_consistent_shape(self):
        url = reverse(URL["category_list"])
        anon = self.client.post(url, {}, format="json")
        self.assertTrue({"detail", "code"} <= set(anon.data))
        self.client.force_authenticate(self.customer)
        forbidden = self.client.post(url, {}, format="json")
        self.assertTrue({"detail", "code"} <= set(forbidden.data))
        self.assertEqual(forbidden.data["code"], "permission_denied")

    def test_invalid_bearer_token_uses_same_shape(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        response = self.client.get(reverse(URL["order_history"]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)


class PublicEndpointTests(APITestCase):
    PUBLIC_AUTH = ("register", "login", "verify_email", "resend_verification",
                   "forgot_password", "reset_password", "token_refresh")

    def setUp(self):
        # forgot/reset-password keep their own throttle; counters live in the
        # (in-process) cache and would otherwise leak between tests.
        cache.clear()

    def test_public_auth_endpoints_reachable_anonymously(self):
        # Empty body -> 400 (validation), i.e. reachable, not 401/403.
        for name in self.PUBLIC_AUTH:
            with self.subTest(endpoint=name):
                response = self.client.post(reverse(URL[name]), {}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_auth_endpoints_ignore_stale_bearer_token(self):
        # A client holding an expired access token must still be able to
        # log in / register. Needs `authentication_classes = ()` on the view.
        self.client.credentials(HTTP_AUTHORIZATION="Bearer expired.or.invalid")
        for name in self.PUBLIC_AUTH:
            with self.subTest(endpoint=name):
                response = self.client.post(reverse(URL[name]), {}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_endpoints_require_authentication(self):
        for name, method in (
            ("order_history", "get"), ("cartitem_list", "get"), ("favorite_list", "get"),
            ("address_list", "get"), ("payment_intent", "post"),
            ("favorite_list", "post"), ("review_list", "post"),
        ):
            with self.subTest(endpoint=name, method=method):
                response = getattr(self.client, method)(reverse(URL[name]), {}, format="json")
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RegistrationPrivilegeTests(APITestCase):
    """Nobody may self-register with elevated privileges."""

    def register(self, **extra):
        payload = {"email": "new@example.com", "password": "Str0ng-pass!123", **extra}
        return self.client.post(reverse(URL["register"]), payload, format="json")

    def test_default_role_is_client(self):
        response = self.register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(User.objects.get(email="new@example.com").role, "CLIENT")

    def test_cannot_register_as_admin(self):
        self.register(role="ADMIN")
        user = User.objects.filter(email="new@example.com").first()
        self.assertTrue(user is None or not is_admin(user), "self-registered admin!")

    def test_cannot_set_staff_flags(self):
        self.register(is_staff=True, is_superuser=True)
        user = User.objects.filter(email="new@example.com").first()
        self.assertTrue(user is None or not (user.is_staff or user.is_superuser))


class OwnershipTests(APITestCase):
    """User A must never reach User B's orders / carts / payments."""

    @classmethod
    def setUpTestData(cls):
        cls.user_a = make_user("a@example.com")
        cls.user_b = make_user("b@example.com")
        cls.admin = make_user("admin@example.com", role="ADMIN")
        cls.restaurant = make_restaurant()
        cls.menu_item = make_menu_item(cls.restaurant)
        cls.order_a = make_order(cls.user_a, cls.restaurant)
        cls.order_b = make_order(cls.user_b, cls.restaurant)
        cls.cart_a = Cart.objects.create(user=cls.user_a, restaurant=cls.restaurant)
        cls.cart_b = Cart.objects.create(user=cls.user_b, restaurant=cls.restaurant)
        cls.item_b = CartItem.objects.create(cart=cls.cart_b, menu_item=cls.menu_item, quantity=1)

    def setUp(self):
        self.client.force_authenticate(self.user_a)

    def test_cannot_read_other_users_order(self):
        response = self.client.get(reverse(URL["order_detail"], kwargs={"pk": self.order_b.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_only_contains_own_orders(self):
        response = self.client.get(reverse(URL["order_history"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([o["id"] for o in rows(response)], [self.order_a.pk])

    def test_customer_cannot_change_order_status(self):
        for order in (self.order_a, self.order_b):
            with self.subTest(order=order.pk):
                response = self.client.patch(reverse(URL["order_status"], kwargs={"pk": order.pk}),
                                             {"status": Order.STATUS_ACCEPTED}, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                order.refresh_from_db()
                self.assertEqual(order.status, Order.STATUS_PENDING)

    def test_customer_can_read_own_status_but_not_others(self):
        own = self.client.get(reverse(URL["order_status"], kwargs={"pk": self.order_a.pk}))
        other = self.client.get(reverse(URL["order_status"], kwargs={"pk": self.order_b.pk}))
        self.assertEqual(own.status_code, status.HTTP_200_OK)
        self.assertEqual(other.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_change_order_status(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(reverse(URL["order_status"], kwargs={"pk": self.order_b.pk}),
                                     {"status": Order.STATUS_ACCEPTED}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.order_b.refresh_from_db()
        self.assertEqual(self.order_b.status, Order.STATUS_ACCEPTED)

    def test_cannot_read_or_modify_other_users_cart_item(self):
        detail = reverse(URL["cartitem_detail"], kwargs={"pk": self.item_b.pk})
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.patch(detail, {"quantity": 99}, format="json").status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.item_b.refresh_from_db()
        self.assertEqual(self.item_b.quantity, 1)

    def test_cannot_add_item_to_other_users_cart(self):
        other_item = make_menu_item(self.restaurant, name="Fries")
        response = self.client.post(reverse(URL["cartitem_list"]),
                                    {"cart": self.cart_b.pk, "menu_item": other_item.pk, "quantity": 1},
                                    format="json")
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(CartItem.objects.filter(cart=self.cart_b, menu_item=other_item).exists())

    def test_cannot_move_own_item_into_other_users_cart(self):
        mine = CartItem.objects.create(cart=self.cart_a, menu_item=self.menu_item, quantity=1)
        response = self.client.patch(reverse(URL["cartitem_detail"], kwargs={"pk": mine.pk}),
                                     {"cart": self.cart_b.pk}, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        mine.refresh_from_db()
        self.assertEqual(mine.cart_id, self.cart_a.pk)

    def test_cannot_create_payment_intent_for_other_users_order(self):
        from payments.models import Payment
        response = self.client.post(reverse(URL["payment_intent"]), {"order_id": self.order_b.pk}, format="json")
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.assertFalse(Payment.objects.filter(order=self.order_b).exists())


class OrderStatusRulesTests(APITestCase):
    """What an administrator may do once they are allowed to change a status."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = make_user("admin@example.com", role="ADMIN")
        cls.client_user = make_user("client@example.com")
        cls.restaurant = make_restaurant()

    def setUp(self):
        self.client.force_authenticate(self.admin)

    def patch_status(self, order, new_status):
        return self.client.patch(reverse(URL["order_status"], kwargs={"pk": order.pk}),
                                 {"status": new_status}, format="json")

    def order(self, status):
        return make_order(self.client_user, self.restaurant, status)

    def test_admin_can_walk_the_normal_lifecycle(self):
        order = self.order(Order.STATUS_PENDING)
        for new_status in (Order.STATUS_ACCEPTED, Order.STATUS_PREPARING, Order.STATUS_READY,
                           Order.STATUS_DELIVERING, Order.STATUS_COMPLETED):
            with self.subTest(status=new_status):
                response = self.patch_status(order, new_status)
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                order.refresh_from_db()
                self.assertEqual(order.status, new_status)

    def test_admin_cannot_push_an_unpaid_order_to_the_kitchen(self):
        order = self.order(Order.STATUS_AWAITING_PAYMENT)
        for new_status in (Order.STATUS_ACCEPTED, Order.STATUS_PREPARING, Order.STATUS_COMPLETED):
            with self.subTest(status=new_status):
                self.assertEqual(self.patch_status(order, new_status).status_code,
                                 status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_AWAITING_PAYMENT)

    def test_admin_can_cancel_an_unpaid_order(self):
        order = self.order(Order.STATUS_AWAITING_PAYMENT)
        self.assertEqual(self.patch_status(order, Order.STATUS_CANCELLED).status_code, status.HTTP_200_OK)

    def test_payment_statuses_cannot_be_set_by_hand(self):
        order = self.order(Order.STATUS_ACCEPTED)
        for new_status in (Order.STATUS_AWAITING_PAYMENT, Order.STATUS_PENDING):
            with self.subTest(status=new_status):
                self.assertEqual(self.patch_status(order, new_status).status_code,
                                 status.HTTP_400_BAD_REQUEST)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_ACCEPTED)

    def test_finished_orders_cannot_be_reopened(self):
        for final in (Order.STATUS_COMPLETED, Order.STATUS_CANCELLED, Order.STATUS_DECLINED):
            with self.subTest(final=final):
                order = self.order(final)
                self.assertEqual(self.patch_status(order, Order.STATUS_ACCEPTED).status_code,
                                 status.HTTP_400_BAD_REQUEST)
                order.refresh_from_db()
                self.assertEqual(order.status, final)

    def test_unknown_status_is_rejected(self):
        order = self.order(Order.STATUS_PENDING)
        self.assertEqual(self.patch_status(order, "BOGUS").status_code, status.HTTP_400_BAD_REQUEST)


class FavoritesOwnershipTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = make_user("a@example.com")
        cls.user_b = make_user("b@example.com")
        cls.restaurant = make_restaurant("R1")
        cls.restaurant2 = make_restaurant("R2")
        cls.fav_b = Favorite.objects.create(user=cls.user_b, restaurant=cls.restaurant)

    def setUp(self):
        self.client.force_authenticate(self.user_a)

    def test_list_only_contains_own_favorites(self):
        response = self.client.get(reverse(URL["favorite_list"]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(rows(response), [])

    def test_cannot_delete_other_users_favorite(self):
        response = self.client.delete(reverse(URL["favorite_detail"], kwargs={"pk": self.fav_b.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Favorite.objects.filter(pk=self.fav_b.pk).exists())

    def test_cannot_create_favorite_on_behalf_of_another_user(self):
        response = self.client.post(reverse(URL["favorite_list"]),
                                    {"restaurant": self.restaurant2.pk, "user": self.user_b.pk},
                                    format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        favorite = Favorite.objects.get(restaurant=self.restaurant2)
        self.assertEqual(favorite.user_id, self.user_a.pk)

    def test_check_endpoint_reflects_only_own_favorites(self):
        response = self.client.get(reverse(URL["favorite_check"]), {"restaurant": self.restaurant.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_favorite"])
        self.assertIsNone(response.data["favorite_id"])


class ReviewPermissionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = make_user("a@example.com")
        cls.user_b = make_user("b@example.com")
        cls.admin = make_user("admin@example.com", role="ADMIN")
        cls.restaurant = make_restaurant("R1")
        cls.restaurant2 = make_restaurant("R2")
        done = Order.STATUS_COMPLETED
        cls.order_a = make_order(cls.user_a, cls.restaurant, done)
        cls.order_a2 = make_order(cls.user_a, cls.restaurant, done)   # no review yet
        cls.order_b = make_order(cls.user_b, cls.restaurant, done)
        cls.review_a = Review.objects.create(client=cls.user_a, restaurant=cls.restaurant,
                                             order=cls.order_a, rating=5, comment="great")
        cls.review_b = Review.objects.create(client=cls.user_b, restaurant=cls.restaurant,
                                             order=cls.order_b, rating=3, comment="ok")

    def test_anonymous_can_read_but_not_write(self):
        self.assertEqual(self.client.get(reverse(URL["review_list"])).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(reverse(URL["review_list"]), {}, format="json").status_code,
                         status.HTTP_401_UNAUTHORIZED)

    def test_reviewer_email_is_not_public(self):
        anonymous = self.client.get(reverse(URL["review_list"]))
        for review in rows(anonymous):
            self.assertNotIn("client_email", review)
        self.client.force_authenticate(self.user_a)
        as_a = {r["id"]: r for r in rows(self.client.get(reverse(URL["review_list"])))}
        self.assertNotIn("client_email", as_a[self.review_b.pk])            # someone else's
        self.assertEqual(as_a[self.review_a.pk]["client_email"], "a@example.com")  # own

    def test_admin_can_see_reviewer_email(self):
        self.client.force_authenticate(self.admin)
        payload = {r["id"]: r for r in rows(self.client.get(reverse(URL["review_list"])))}
        self.assertEqual(payload[self.review_b.pk]["client_email"], "b@example.com")

    def test_cannot_modify_or_delete_other_users_review(self):
        self.client.force_authenticate(self.user_a)
        detail = reverse(URL["review_detail"], kwargs={"pk": self.review_b.pk})
        for method, body in (("patch", {"rating": 1}), ("put", {"rating": 1}), ("delete", None)):
            with self.subTest(method=method):
                response = getattr(self.client, method)(detail, body, format="json")
                self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        self.review_b.refresh_from_db()
        self.assertEqual(self.review_b.rating, 3)

    def test_cannot_review_other_users_order(self):
        self.client.force_authenticate(self.user_a)
        other_order = make_order(self.user_b, self.restaurant, Order.STATUS_COMPLETED)
        response = self.client.post(reverse(URL["review_list"]),
                                    {"order": other_order.pk, "restaurant": self.restaurant.pk,
                                     "rating": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Review.objects.filter(order=other_order).exists())

    def test_owner_can_edit_rating(self):
        self.client.force_authenticate(self.user_a)
        response = self.client.patch(reverse(URL["review_detail"], kwargs={"pk": self.review_a.pk}),
                                     {"rating": 4}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.review_a.refresh_from_db()
        self.assertEqual(self.review_a.rating, 4)

    def test_owner_cannot_repoint_review_to_another_order_or_restaurant(self):
        self.client.force_authenticate(self.user_a)
        detail = reverse(URL["review_detail"], kwargs={"pk": self.review_a.pk})
        for body in ({"order": self.order_a2.pk}, {"restaurant": self.restaurant2.pk}):
            with self.subTest(body=body):
                response = self.client.patch(detail, body, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.review_a.refresh_from_db()
        self.assertEqual(self.review_a.order_id, self.order_a.pk)
        self.assertEqual(self.review_a.restaurant_id, self.restaurant.pk)


class AddressOwnershipTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_a = make_user("a@example.com")
        cls.user_b = make_user("b@example.com")
        cls.address_b = DeliveryAddress.objects.create(
            user=cls.user_b, label="Home", formatted_address="B street 2",
            street="B street", building="2", is_default=True,
        )

    def setUp(self):
        self.client.force_authenticate(self.user_a)

    def test_list_only_contains_own_addresses(self):
        self.assertEqual(rows(self.client.get(reverse(URL["address_list"]))), [])

    def test_cannot_read_modify_or_delete_other_users_address(self):
        detail = reverse(URL["address_detail"], kwargs={"pk": self.address_b.pk})
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.patch(detail, {"label": "x"}, format="json").status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_404_NOT_FOUND)
        self.address_b.refresh_from_db()
        self.assertEqual(self.address_b.label, "Home")

    def test_cannot_set_other_users_address_as_default(self):
        response = self.client.post(reverse(URL["address_set_default"], kwargs={"pk": self.address_b.pk}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_default_address_endpoint_never_returns_others_address(self):
        self.assertEqual(self.client.get(reverse(URL["address_default"])).status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_cannot_create_address_for_another_user(self):
        response = self.client.post(reverse(URL["address_list"]), {
            "label": "Mine", "formatted_address": "A street 1", "street": "A street",
            "building": "1", "user": self.user_b.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(DeliveryAddress.objects.get(label="Mine").user_id, self.user_a.pk)


def stripe_signature(payload, secret):
    timestamp = int(time.time())
    digest = hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


@override_settings(STRIPE_WEBHOOK_SECRET="whsec_unit_test_secret")
class StripeWebhookTests(APITestCase):
    """Reachable without JWT, but ONLY with a valid Stripe signature."""

    @classmethod
    def setUpTestData(cls):
        from payments.models import Payment
        cls.user = make_user("payer@example.com")
        cls.restaurant = make_restaurant()
        cls.order = make_order(cls.user, cls.restaurant, Order.STATUS_AWAITING_PAYMENT)
        cls.payment = Payment.objects.create(order=cls.order, stripe_payment_intent_id="pi_test_123",
                                             amount=Decimal("10.00"), currency="uah")

    def event(self, event_id="evt_test_1"):
        return json.dumps({
            "id": event_id, "object": "event", "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_test_123", "object": "payment_intent"}},
        })

    def post(self, payload, signature=None, **extra):
        headers = {"HTTP_STRIPE_SIGNATURE": signature} if signature else {}
        return self.client.post(reverse(URL["webhook"]), data=payload,
                                content_type="application/json", **headers, **extra)

    def assert_order_unchanged(self):
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_AWAITING_PAYMENT)

    def test_missing_signature_is_rejected(self):
        self.assertEqual(self.post(self.event()).status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_order_unchanged()

    def test_signature_made_with_wrong_secret_is_rejected(self):
        payload = self.event()
        response = self.post(payload, stripe_signature(payload, "whsec_attacker_guess"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assert_order_unchanged()

    def test_valid_signature_is_accepted_without_jwt(self):
        payload = self.event()
        response = self.post(payload, stripe_signature(payload, "whsec_unit_test_secret"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PENDING)   # paid -> moved on

    def test_valid_signature_ignores_stale_authorization_header(self):
        # Needs `authentication_classes = ()` on StripeWebhookView.
        payload = self.event("evt_test_2")
        response = self.post(payload, stripe_signature(payload, "whsec_unit_test_secret"),
                             HTTP_AUTHORIZATION="Bearer expired.or.invalid")
        self.assertEqual(response.status_code, status.HTTP_200_OK)