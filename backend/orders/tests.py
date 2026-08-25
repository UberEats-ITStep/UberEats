from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cart.models import Cart, CartItem
from restaurants.models import Category, Cuisine, MenuItem, Restaurant

from orders.models import Order, OrderItem
from orders.simulation import simulate_order_lifecycle


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

        self.restaurant = Restaurant.objects.create(
            name='Pizza House',
            cuisine=self.cuisine,
        )

        self.category = Category.objects.create(name='Pizza')

        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Margherita',
            price=Decimal('10.50'),
        )

        self.checkout_url = reverse('order_checkout')
        self.history_url = reverse('order_history')

    def create_order(self, user):
        order = Order.objects.create(
            client=user,
            restaurant=self.restaurant,
            total_price=self.menu_item.price,
            street='Soborna Street',
            building='15A',
            apartment='25',
            entrance='2',
            floor=5,
            delivery_notes='Call before delivery',
            contact_phone='+380501234567',
        )

        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=1,
            price=self.menu_item.price,
        )

        return order

    def valid_checkout_data(self):
        return {
            'street': 'Soborna Street',
            'building': '15A',
            'apartment': '25',
            'entrance': '2',
            'floor': 5,
            'delivery_notes': 'Call before delivery',
            'contact_phone': '+380501234567',
        }

    def add_cart_item(self, quantity=1):
        cart, _ = Cart.objects.get_or_create(user=self.user)

        CartItem.objects.create(
            cart=cart,
            menu_item=self.menu_item,
            quantity=quantity,
        )

        return cart

    def test_checkout_creates_order(self):
        cart = self.add_cart_item(quantity=2)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            self.valid_checkout_data(),
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

        self.assertEqual(order.street, 'Soborna Street')
        self.assertEqual(order.building, '15A')
        self.assertEqual(order.apartment, '25')
        self.assertEqual(order.entrance, '2')
        self.assertEqual(order.floor, 5)
        self.assertEqual(order.delivery_notes, 'Call before delivery')
        self.assertEqual(order.contact_phone, '+380501234567')

        self.assertEqual(response.data['total_price'], '21.00')

    def test_checkout_rejects_empty_items(self):
        Cart.objects.get_or_create(user=self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            self.valid_checkout_data(),
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            response.data['non_field_errors'][0],
            'Your cart is empty.',
        )

        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_requires_street(self):
        self.add_cart_item()

        data = self.valid_checkout_data()
        data.pop('street')

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn('street', response.data)

    def test_checkout_requires_building(self):
        self.add_cart_item()

        data = self.valid_checkout_data()
        data.pop('building')

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn('building', response.data)

    def test_checkout_allows_optional_delivery_fields_to_be_omitted(self):
        self.add_cart_item()

        data = {
            'street': 'Soborna Street',
            'building': '15A',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get()

        self.assertEqual(order.street, 'Soborna Street')
        self.assertEqual(order.building, '15A')
        self.assertEqual(order.apartment, '')
        self.assertEqual(order.entrance, '')
        self.assertIsNone(order.floor)
        self.assertEqual(order.delivery_notes, '')
        self.assertEqual(order.contact_phone, '')

    def test_checkout_rejects_invalid_floor(self):
        self.add_cart_item()

        data = self.valid_checkout_data()
        data['floor'] = -1

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn('floor', response.data)

    def test_checkout_rejects_excessively_high_floor(self):
        self.add_cart_item()

        data = self.valid_checkout_data()
        data['floor'] = 101

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn('floor', response.data)

    def test_checkout_rejects_excessively_long_delivery_notes(self):
        self.add_cart_item()

        data = self.valid_checkout_data()
        data['delivery_notes'] = 'A' * 501

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.checkout_url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn('delivery_notes', response.data)

    def test_order_history_returns_user_orders(self):
        order = self.create_order(self.user)

        self.create_order(self.other_user)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.history_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)

    def test_user_can_view_complete_order_details(self):
        order = self.create_order(self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('order_detail', args=[order.id])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['restaurant_name'],
            self.restaurant.name,
        )

        self.assertEqual(
            response.data['items'][0]['menu_item_name'],
            self.menu_item.name,
        )

        self.assertEqual(
            response.data['items'][0]['subtotal'],
            '10.50',
        )

    def test_user_cannot_view_another_users_order_details(self):
        order = self.create_order(self.other_user)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('order_detail', args=[order.id])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_can_read_order_status(self):
        order = self.create_order(self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse('order_status', args=[order.id])
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data,
            {
                'id': order.id,
                'status': Order.STATUS_PENDING,
            },
        )

    def test_user_cannot_update_order_status(self):
        order = self.create_order(self.user)

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse('order_status', args=[order.id]),
            {'status': Order.STATUS_ACCEPTED},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.STATUS_PENDING,
        )

    def test_admin_can_update_order_status(self):
        order = self.create_order(self.user)

        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('order_status', args=[order.id]),
            {'status': Order.STATUS_ACCEPTED},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.STATUS_ACCEPTED,
        )


class OrderSimulationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='simuser',
            email='sim@example.com',
            password='pwd',
        )

        self.cuisine = Cuisine.objects.create(
            name='Mexican',
        )

        self.restaurant = Restaurant.objects.create(
            name='Taco Place',
            cuisine=self.cuisine,
        )

        self.category = Category.objects.create(
            name='Tacos',
        )

        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Taco',
            price=Decimal('5.00'),
        )

    def create_order(self):
        order = Order.objects.create(
            client=self.user,
            restaurant=self.restaurant,
            total_price=self.menu_item.price,
            street='Main Street',
            building='10',
        )

        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=1,
            price=self.menu_item.price,
        )

        return order

    @patch('orders.simulation.time.sleep', return_value=None)
    def test_simulation_progresses_order_to_completed(self, mock_sleep):
        order = self.create_order()

        self.assertEqual(
            order.status,
            Order.STATUS_PENDING,
        )

        simulate_order_lifecycle(order.id)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.STATUS_COMPLETED,
        )

    @patch('orders.simulation.time.sleep', return_value=None)
    def test_simulation_stops_if_externally_modified(self, mock_sleep):
        order = self.create_order()

        order.status = Order.STATUS_CANCELLED
        order.save()

        simulate_order_lifecycle(order.id)

        order.refresh_from_db()

        self.assertEqual(
            order.status,
            Order.STATUS_CANCELLED,
        )