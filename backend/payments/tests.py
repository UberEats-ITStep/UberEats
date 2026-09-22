import json
from decimal import Decimal
from unittest.mock import patch, MagicMock

import stripe
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from restaurants.models import Restaurant, MenuItem
from orders.models import Order
from cart.models import Cart, CartItem
from payments.models import Payment, StripeWebhookEvent

class PaymentTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='test1@example.com', password='password123', first_name='Test', last_name='User1')
        self.user2 = User.objects.create_user(username='user2', email='test2@example.com', password='password123', first_name='Test', last_name='User2')
        
        from restaurants.models import Cuisine, Category
        self.cuisine = Cuisine.objects.create(name='Test Cuisine')
        self.category = Category.objects.create(name='Test Category')
        self.restaurant = Restaurant.objects.create(name='Test Rest', address='123 St', cuisine=self.cuisine)
        
        self.order1 = Order.objects.create(
            client=self.user1,
            restaurant=self.restaurant,
            total_price=Decimal('150.50'),
            street='Main St',
            building='1'
        )
        self.order2 = Order.objects.create(
            client=self.user2,
            restaurant=self.restaurant,
            total_price=Decimal('200.00'),
            street='Main St',
            building='2'
        )

    @patch('stripe.PaymentIntent.create')
    def test_create_intent_success(self, mock_stripe_create):
        mock_stripe_create.return_value = MagicMock(id='pi_123', client_secret='secret_123')
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('create-intent')
        response = self.client.post(url, {'order_id': self.order1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client_secret'], 'secret_123')
        
        # Check DB
        payment = Payment.objects.get(order=self.order1)
        self.assertEqual(payment.stripe_payment_intent_id, 'pi_123')
        self.assertEqual(payment.amount, Decimal('150.50'))
        
        # Check Stripe got called with kopecks
        mock_stripe_create.assert_called_once()
        args, kwargs = mock_stripe_create.call_args
        self.assertEqual(kwargs['amount'], 15050)
        self.assertEqual(kwargs['currency'], 'uah')

    def test_create_intent_unauthenticated(self):
        url = reverse('create-intent')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_intent_wrong_user(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('create-intent')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('stripe.PaymentIntent.retrieve')
    @patch('stripe.PaymentIntent.create')
    def test_idempotency_reuse_existing_intent(self, mock_create, mock_retrieve):
        # Create existing payment
        Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_existing',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_PENDING
        )
        mock_retrieve.return_value = MagicMock(id='pi_existing', client_secret='secret_existing', status='requires_payment_method')
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('create-intent')
        response = self.client.post(url, {'order_id': self.order1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['client_secret'], 'secret_existing')
        mock_retrieve.assert_called_once_with('pi_existing')
        mock_create.assert_not_called()

    @patch('stripe.PaymentIntent.retrieve')
    def test_reject_already_paid(self, mock_retrieve):
        Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_done',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_SUCCEEDED
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse('create-intent')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already been successfully paid", response.data[0])

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_succeeded(self, mock_construct):
        from django.test import override_settings
        with override_settings(STRIPE_WEBHOOK_SECRET='mock_secret'):
            payment = Payment.objects.create(
                order=self.order1,
                stripe_payment_intent_id='pi_123',
                amount=Decimal('150.50'),
                currency='uah',
                status=Payment.STATUS_PENDING
            )
            
            mock_event = {
                'id': 'evt_123',
                'type': 'payment_intent.succeeded',
                'data': {'object': {'id': 'pi_123'}}
            }
            
            class MockEvent:
                def __init__(self, e):
                    self.id = e['id']
                    self.type = e['type']
                    self.data = MagicMock(object=e['data']['object'])
                    self.dict = e
                def __getitem__(self, key):
                    return self.dict[key]
                    
            mock_construct.return_value = MockEvent(mock_event)

            url = reverse('webhook')
            response = self.client.post(url, '{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='sig')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            payment.refresh_from_db()
            self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)
            
            # Check idempotency record
            self.assertTrue(StripeWebhookEvent.objects.filter(stripe_event_id='evt_123').exists())

    @patch('stripe.Webhook.construct_event')
    def test_webhook_idempotency(self, mock_construct):
        from django.test import override_settings
        with override_settings(STRIPE_WEBHOOK_SECRET='mock_secret'):
            # Seed an already processed event
            StripeWebhookEvent.objects.create(stripe_event_id='evt_duplicate', event_type='payment_intent.succeeded')
            
            mock_event = {
                'id': 'evt_duplicate',
                'type': 'payment_intent.succeeded',
                'data': {'object': {'id': 'pi_123'}}
            }
            
            class MockEvent:
                def __init__(self, e):
                    self.id = e['id']
                    self.type = e['type']
                    self.data = MagicMock(object=e['data']['object'])
                    self.dict = e
                def __getitem__(self, key):
                    return self.dict[key]
                    
            mock_construct.return_value = MockEvent(mock_event)

            url = reverse('webhook')
            response = self.client.post(url, '{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='sig')
            
            # Should return 200 early
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], 'already processed')

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_succeeded_transitions_order_and_clears_cart(self, mock_construct):
        from django.test import override_settings
        with override_settings(STRIPE_WEBHOOK_SECRET='mock_secret'):
            # Set order to AWAITING_PAYMENT
            self.order1.status = Order.STATUS_AWAITING_PAYMENT
            self.order1.save()

            # Create user's cart with an item
            cart, _ = Cart.objects.get_or_create(user=self.user1)
            menu_item = MenuItem.objects.create(restaurant=self.restaurant, category=self.category, name='Burger', price=Decimal('15.00'))
            CartItem.objects.create(cart=cart, menu_item=menu_item, quantity=2)
            self.assertEqual(CartItem.objects.filter(cart=cart).count(), 1)

            payment = Payment.objects.create(
                order=self.order1,
                stripe_payment_intent_id='pi_success_test',
                amount=Decimal('150.50'),
                currency='uah',
                status=Payment.STATUS_PENDING
            )

            mock_event = {
                'id': 'evt_success_test',
                'type': 'payment_intent.succeeded',
                'data': {'object': {'id': 'pi_success_test'}}
            }

            class MockEvent:
                def __init__(self, e):
                    self.id = e['id']
                    self.type = e['type']
                    self.data = MagicMock(object=e['data']['object'])
                    self.dict = e
                def __getitem__(self, key):
                    return self.dict[key]

            mock_construct.return_value = MockEvent(mock_event)

            url = reverse('webhook')
            response = self.client.post(url, '{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='sig')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            payment.refresh_from_db()
            self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)

            # Order must transition to PENDING (confirmed)
            self.order1.refresh_from_db()
            self.assertEqual(self.order1.status, Order.STATUS_PENDING)

            # Cart must be cleared
            self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_payment_failed_cancels_order_and_preserves_cart(self, mock_construct):
        from django.test import override_settings
        with override_settings(STRIPE_WEBHOOK_SECRET='mock_secret'):
            self.order1.status = Order.STATUS_AWAITING_PAYMENT
            self.order1.save()

            cart, _ = Cart.objects.get_or_create(user=self.user1)
            menu_item = MenuItem.objects.create(restaurant=self.restaurant, category=self.category, name='Pizza', price=Decimal('20.00'))
            CartItem.objects.create(cart=cart, menu_item=menu_item, quantity=1)

            payment = Payment.objects.create(
                order=self.order1,
                stripe_payment_intent_id='pi_fail_test',
                amount=Decimal('150.50'),
                currency='uah',
                status=Payment.STATUS_PENDING
            )

            mock_event = {
                'id': 'evt_fail_test',
                'type': 'payment_intent.payment_failed',
                'data': {'object': {'id': 'pi_fail_test'}}
            }

            class MockEvent:
                def __init__(self, e):
                    self.id = e['id']
                    self.type = e['type']
                    self.data = MagicMock(object=e['data']['object'])
                    self.dict = e
                def __getitem__(self, key):
                    return self.dict[key]

            mock_construct.return_value = MockEvent(mock_event)

            url = reverse('webhook')
            response = self.client.post(url, '{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='sig')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            payment.refresh_from_db()
            self.assertEqual(payment.status, Payment.STATUS_FAILED)

            # Order must transition to DECLINED
            self.order1.refresh_from_db()
            self.assertEqual(self.order1.status, Order.STATUS_DECLINED)

            # Cart must remain intact!
            self.assertEqual(CartItem.objects.filter(cart=cart).count(), 1)

    @patch('stripe.PaymentIntent.retrieve')
    def test_payment_failed_endpoint_cancels_order_and_preserves_cart(self, mock_retrieve):
        mock_retrieve.return_value = MagicMock(status='requires_payment_method')
        self.order1.status = Order.STATUS_AWAITING_PAYMENT
        self.order1.save()

        cart, _ = Cart.objects.get_or_create(user=self.user1)
        menu_item = MenuItem.objects.create(restaurant=self.restaurant, category=self.category, name='Salad', price=Decimal('10.00'))
        CartItem.objects.create(cart=cart, menu_item=menu_item, quantity=1)

        Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_decline_test',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_PENDING
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse('payment-failed')
        response = self.client.post(url, {
            'order_id': self.order1.id,
            'error_message': 'The payment was declined. See details in your bank provider.'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'declined')

        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, Order.STATUS_DECLINED)

        payment = Payment.objects.get(order=self.order1)
        self.assertEqual(payment.status, Payment.STATUS_FAILED)

        # Cart is NOT deleted
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 1)

        # Verify declined order does NOT appear in OrderHistoryView (order page)
        history_url = reverse('order_history')
        history_response = self.client.get(history_url)
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        order_ids = [o['id'] for o in history_response.data]
        self.assertNotIn(self.order1.id, order_ids)

    def test_payment_failed_endpoint_forbidden_for_other_user(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('payment-failed')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_payment_failed_rejects_if_payment_already_succeeded(self):
        Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_already_paid',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_SUCCEEDED
        )
        self.client.force_authenticate(user=self.user1)
        url = reverse('payment-failed')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order1.refresh_from_db()
        self.assertNotEqual(self.order1.status, Order.STATUS_DECLINED)

    def test_payment_failed_rejects_if_payment_processing(self):
        Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_processing_test',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_PROCESSING
        )
        self.client.force_authenticate(user=self.user1)
        url = reverse('payment-failed')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order1.refresh_from_db()
        self.assertNotEqual(self.order1.status, Order.STATUS_DECLINED)

    @patch('stripe.PaymentIntent.retrieve')
    def test_payment_failed_rejects_if_stripe_reports_succeeded(self, mock_retrieve):
        mock_retrieve.return_value = MagicMock(status='succeeded')
        payment = Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_stripe_succeeded',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_PENDING
        )
        self.client.force_authenticate(user=self.user1)
        url = reverse('payment-failed')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_SUCCEEDED)
        self.order1.refresh_from_db()
        self.assertNotEqual(self.order1.status, Order.STATUS_DECLINED)

    @patch('stripe.PaymentIntent.retrieve')
    def test_payment_failed_rejects_if_stripe_reports_processing(self, mock_retrieve):
        mock_retrieve.return_value = MagicMock(status='processing')
        payment = Payment.objects.create(
            order=self.order1,
            stripe_payment_intent_id='pi_stripe_processing',
            amount=Decimal('150.50'),
            currency='uah',
            status=Payment.STATUS_PENDING
        )
        self.client.force_authenticate(user=self.user1)
        url = reverse('payment-failed')
        response = self.client.post(url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_PROCESSING)
        self.order1.refresh_from_db()
        self.assertNotEqual(self.order1.status, Order.STATUS_DECLINED)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_handles_stripe_object_serialization(self, mock_construct):
        from django.test import override_settings
        with override_settings(STRIPE_WEBHOOK_SECRET='mock_secret'):
            Payment.objects.create(
                order=self.order1,
                stripe_payment_intent_id='pi_serialize_test',
                amount=Decimal('150.50'),
                currency='uah',
                status=Payment.STATUS_PENDING
            )

            # Create an actual stripe PaymentIntent object
            stripe_obj = stripe.PaymentIntent.construct_from({
                'id': 'pi_serialize_test',
                'amount': 15050,
                'currency': 'uah',
                'status': 'succeeded'
            }, key='mock_key')

            mock_event = {
                'id': 'evt_serialize_test',
                'type': 'payment_intent.succeeded',
                'data': {'object': stripe_obj}
            }

            class MockEvent:
                def __init__(self, e):
                    self.id = e['id']
                    self.type = e['type']
                    self.data = MagicMock(object=stripe_obj)
                    self.dict = e
                def __getitem__(self, key):
                    return self.dict[key]

            mock_construct.return_value = MockEvent(mock_event)

            url = reverse('webhook')
            response = self.client.post(url, '{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='sig')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            event_record = StripeWebhookEvent.objects.get(stripe_event_id='evt_serialize_test')
            self.assertEqual(event_record.payload.get('id'), 'pi_serialize_test')

