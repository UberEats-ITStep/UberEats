from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import Category, MenuItem, Restaurant

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

        self.restaurant = Restaurant.objects.create(
            name='Pizza House',
            description='Stone-baked pizza and Italian favourites.',
            rating=4.6,
            delivery_time='25-40 min',
            image='https://example.com/pizza-house.jpg',
        )
        category = Category.objects.create(restaurant=self.restaurant, name='Pizza')
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=category,
            name='Margherita',
            price=Decimal('10.50'),
        )
        self.checkout_url = reverse('order_checkout')
        self.history_url = reverse('order_history')

    def create_order(self, user, *, quantity=1, status=Order.STATUS_PENDING):
        order = Order.objects.create(
            user=user,
            status=status,
            total_price=self.menu_item.price * quantity,
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=quantity,
            price=self.menu_item.price,
        )
        return order

    def test_checkout_creates_order(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            {
                'delivery_address': 'Kyiv, Main street 1',
                'items': [
                    {
                        'menu_item': self.menu_item.id,
                        'quantity': 2,
                    },
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        order = Order.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.total_price, Decimal('21.00'))
        self.assertEqual(response.data['total_price'], '21.00')

    def test_checkout_rejects_empty_items(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            {
                'items': [],
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_order_history_returns_a_full_summary_for_the_current_user(self):
        order = self.create_order(
            self.user,
            quantity=2,
            status=Order.STATUS_PREPARING,
        )
        self.create_order(self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)
        self.assertEqual(response.data[0]['restaurantName'], 'Pizza House')
        self.assertEqual(response.data[0]['status'], Order.STATUS_PREPARING)
        self.assertEqual(response.data[0]['totalPrice'], '21.00')
        self.assertIn('createdAt', response.data[0])
        self.assertEqual(response.data[0]['itemCount'], 2)
        self.assertEqual(response.data[0]['items'], [{
            'id': order.items.get().id,
            'menuItemId': self.menu_item.id,
            'name': 'Margherita',
            'quantity': 2,
            'price': '10.50',
        }])

    def test_order_history_returns_newest_orders_first(self):
        older_order = self.create_order(self.user)
        newer_order = self.create_order(self.user)
        now = timezone.now()
        Order.objects.filter(pk=older_order.pk).update(created_at=now - timedelta(days=1))
        Order.objects.filter(pk=newer_order.pk).update(created_at=now)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [order['id'] for order in response.data],
            [newer_order.id, older_order.id],
        )

    def test_order_history_requires_authentication(self):
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
            {'status': Order.STATUS_READY},
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
            {'status': Order.STATUS_READY},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_READY)