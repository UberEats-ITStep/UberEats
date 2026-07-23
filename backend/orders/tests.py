from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import Category, Cuisine, MenuItem, Restaurant

from cart.models import Cart, CartItem
from .models import Order, OrderItem


User = get_user_model()


class OrderCheckoutApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='TestPass123!',
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='TestPass123!',
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='TestPass123!',
            role='Admin',
        )

        self.cuisine = Cuisine.objects.create(name='Italian')
        self.restaurant = Restaurant.objects.create(name='Pizza House', cuisine=self.cuisine)
        category = Category.objects.create(name='Pizza')
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=category,
            name='Margherita',
            price=Decimal('10.50'),
        )
        self.checkout_url = reverse('order_checkout')
        self.history_url = reverse('order_history')

    def create_order(self, user):
        order = Order.objects.create(client=user, restaurant=self.restaurant, total_price=self.menu_item.price)
        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=1,
            price=self.menu_item.price,
        )
        return order

    def test_checkout_creates_order(self):
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=cart, menu_item=self.menu_item, quantity=2)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            {
                'delivery_address': 'Kyiv, Main street 1',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)

        order = Order.objects.get()
        self.assertEqual(order.client, self.user)
        self.assertEqual(order.restaurant, self.restaurant)
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.total_price, Decimal('21.00'))
        self.assertEqual(response.data['total_price'], '21.00')

    def test_checkout_rejects_empty_items(self):
        Cart.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            {
                'delivery_address': 'Kyiv, Main street 1',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Your cart is empty.')
        self.assertEqual(Order.objects.count(), 0)

    def test_order_history_returns_user_orders(self):
        order = self.create_order(self.user)
        self.create_order(self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)

    def test_user_can_read_order_status(self):
        order = self.create_order(self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('order_status', args=[order.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'id': order.id, 'status': Order.STATUS_PENDING})

    def test_user_cannot_update_order_status(self):
        order = self.create_order(self.user)
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse('order_status', args=[order.id]),
            {'status': Order.STATUS_ACCEPTED},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PENDING)

    def test_admin_can_update_order_status(self):
        order = self.create_order(self.user)
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('order_status', args=[order.id]),
            {'status': Order.STATUS_ACCEPTED},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_ACCEPTED)
        
