import stripe
import logging
from django.conf import settings
from django.db import transaction, IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404

from .models import Payment, StripeWebhookEvent
from orders.models import Order
from .serializers import CreateIntentRequestSerializer, CreateIntentResponseSerializer
from .services import create_or_retrieve_payment_intent

logger = logging.getLogger(__name__)

class CreatePaymentIntentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        req_serializer = CreateIntentRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        order_id = req_serializer.validated_data['order_id']
        
        with transaction.atomic():
            # Validate order exists, lock row, and check permissions
            order = get_object_or_404(Order.objects.select_for_update(), id=order_id)
            if order.client != request.user:
                return Response(
                    {"detail": "You do not have permission to pay for this order."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            client_secret = create_or_retrieve_payment_intent(order)
        
        res_serializer = CreateIntentResponseSerializer({"client_secret": client_secret})
        return Response(res_serializer.data, status=status.HTTP_200_OK)


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        
        if not webhook_secret:
            logger.error("STRIPE_WEBHOOK_SECRET is not configured.")
            return Response("Webhook secret not configured", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            return Response("Invalid payload", status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response("Invalid signature", status=status.HTTP_400_BAD_REQUEST)

        # Idempotency lock via database unique constraint on stripe_event_id
        try:
            # Safely serialize StripeObject or dict to JSON-compatible dict
            obj_data = {}
            if hasattr(event, 'data') and hasattr(event.data, 'object'):
                raw_obj = event.data.object
                if hasattr(raw_obj, 'to_dict'):
                    obj_data = raw_obj.to_dict()
                elif isinstance(raw_obj, dict):
                    obj_data = raw_obj

            with transaction.atomic():
                webhook_record = StripeWebhookEvent.objects.create(
                    stripe_event_id=event['id'],
                    event_type=event['type'],
                    payload=obj_data
                )
                self.process_event(event)
        except IntegrityError:
            logger.info(f"StripeWebhookEvent {event['id']} already processed. Ignoring.")
            return Response({"status": "already processed"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error processing webhook event {event['id']}: {str(e)}")
            return Response("Internal server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    def process_event(self, event):
        event_type = event['type']
        raw_obj = event['data']['object']
        obj = raw_obj.to_dict() if hasattr(raw_obj, 'to_dict') else (dict(raw_obj) if isinstance(raw_obj, dict) else {})
        
        if event_type.startswith('payment_intent.'):
            intent_id = obj.get('id')
            if not intent_id:
                return

            try:
                payment = Payment.objects.select_for_update().get(stripe_payment_intent_id=intent_id)
            except Payment.DoesNotExist:
                logger.warning(f"Webhook received for unknown PaymentIntent: {intent_id}")
                return

            if event_type == 'payment_intent.succeeded':
                payment.status = Payment.STATUS_SUCCEEDED
                payment.save(update_fields=['status', 'updated_at'])

                order = payment.order
                if order.status == Order.STATUS_AWAITING_PAYMENT:
                    order.status = Order.STATUS_PENDING
                    order.save(update_fields=['status'])

                    # Trigger restaurant simulation if running in DEBUG mode
                    if getattr(settings, 'DEBUG', False):
                        import threading
                        from orders.simulation import simulate_order_lifecycle
                        threading.Thread(
                            target=simulate_order_lifecycle,
                            args=(order.id,),
                            daemon=True
                        ).start()

                # Always clear user's cart now that order is successfully paid
                from cart.models import CartItem
                CartItem.objects.filter(cart__user=order.client).delete()

            elif event_type == 'payment_intent.payment_failed':
                payment.status = Payment.STATUS_FAILED
                payment.save(update_fields=['status', 'updated_at'])

                order = payment.order
                if order.status in (Order.STATUS_PENDING, Order.STATUS_AWAITING_PAYMENT):
                    order.status = Order.STATUS_DECLINED
                    order.save(update_fields=['status'])

                    from cart.models import Cart, CartItem
                    cart, _ = Cart.objects.get_or_create(user=order.client)
                    for item in order.items.all():
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            menu_item=item.menu_item,
                            defaults={'quantity': item.quantity}
                        )
                        if not created:
                            cart_item.quantity = max(cart_item.quantity, item.quantity)
                            cart_item.save(update_fields=['quantity'])

            elif event_type == 'payment_intent.canceled':
                payment.status = Payment.STATUS_CANCELED
                payment.save(update_fields=['status', 'updated_at'])

                order = payment.order
                if order.status in (Order.STATUS_PENDING, Order.STATUS_AWAITING_PAYMENT):
                    order.status = Order.STATUS_DECLINED
                    order.save(update_fields=['status'])

                    from cart.models import Cart, CartItem
                    cart, _ = Cart.objects.get_or_create(user=order.client)
                    for item in order.items.all():
                        cart_item, created = CartItem.objects.get_or_create(
                            cart=cart,
                            menu_item=item.menu_item,
                            defaults={'quantity': item.quantity}
                        )
                        if not created:
                            cart_item.quantity = max(cart_item.quantity, item.quantity)
                            cart_item.save(update_fields=['quantity'])

            elif event_type == 'payment_intent.processing':
                payment.status = Payment.STATUS_PROCESSING
                payment.save(update_fields=['status', 'updated_at'])


class PaymentFailedView(APIView):
    """
    Endpoint called immediately by frontend when a card is declined
    or Stripe payment confirmation fails. Immediately marks the order
    as DECLINED and payment as FAILED, restoring the user's cart so they can retry.
    Guarantees that payments already SUCCEEDED or PROCESSING cannot be falsely failed.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({"detail": "order_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = get_object_or_404(Order.objects.select_for_update(), id=order_id)
            if order.client != request.user:
                return Response(
                    {"detail": "You do not have permission to modify this order."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Prevent declining orders that have progressed beyond pending/awaiting
            if order.status not in (Order.STATUS_PENDING, Order.STATUS_AWAITING_PAYMENT):
                return Response(
                    {"detail": f"Order cannot be declined from its current status: {order.status}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check payment state authority: Stripe is authoritative
            if hasattr(order, 'payment'):
                payment = order.payment
                if payment.status in (Payment.STATUS_SUCCEEDED, Payment.STATUS_PROCESSING):
                    return Response(
                        {"detail": f"Cannot decline order with payment in status {payment.status}."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Verify against Stripe API if secret key and intent ID are present
                if getattr(settings, 'STRIPE_SECRET_KEY', None) and payment.stripe_payment_intent_id:
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    try:
                        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                        if intent.status == 'succeeded':
                            payment.status = Payment.STATUS_SUCCEEDED
                            payment.save(update_fields=['status', 'updated_at'])
                            return Response(
                                {"detail": "Cannot decline order: payment already succeeded on Stripe."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        elif intent.status == 'processing':
                            payment.status = Payment.STATUS_PROCESSING
                            payment.save(update_fields=['status', 'updated_at'])
                            return Response(
                                {"detail": "Cannot decline order: payment is currently processing on Stripe."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    except stripe.error.StripeError as e:
                        logger.warning(f"Could not verify PaymentIntent with Stripe: {e}")

                payment.status = Payment.STATUS_FAILED
                payment.save(update_fields=['status', 'updated_at'])

            error_message = request.data.get(
                'error_message',
                'The payment was declined. See details in your bank provider.'
            )

            order.status = Order.STATUS_DECLINED
            order.save(update_fields=['status'])

            # Restore cart items so user can retry with another card
            from cart.models import Cart, CartItem
            cart, _ = Cart.objects.get_or_create(user=order.client)
            if not cart.restaurant:
                cart.restaurant = order.restaurant
                cart.save(update_fields=['restaurant'])

            for item in order.items.all():
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    menu_item=item.menu_item,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    cart_item.quantity = max(cart_item.quantity, item.quantity)
                    cart_item.save(update_fields=['quantity'])

        return Response({
            "status": "declined",
            "order_id": order.id,
            "detail": error_message
        }, status=status.HTTP_200_OK)
