import stripe
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from .models import Payment
from orders.models import Order
from rest_framework.exceptions import ValidationError

PAYMENT_CURRENCY = getattr(settings, 'PAYMENT_CURRENCY', 'uah')

def convert_to_stripe_amount(amount_decimal: Decimal) -> int:
    """Safely convert Decimal amount to Stripe's minor unit (e.g. kopecks/cents)"""
    return int((amount_decimal * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def create_or_retrieve_payment_intent(order: Order) -> str:
    """
    Creates a Stripe PaymentIntent for the given Order and returns its client_secret.
    If a Payment already exists, re-verifies it and returns its intent.
    Guarantees idempotency via Stripe's Idempotency-Key.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    currency = getattr(settings, 'PAYMENT_CURRENCY', 'uah').lower()

    # 1. Check if Order is valid for payment
    if order.status not in (Order.STATUS_AWAITING_PAYMENT, Order.STATUS_PENDING):
        raise ValidationError("Order is not in a valid state for payment.")
    
    # 2. Re-check if Payment already exists
    if hasattr(order, 'payment'):
        payment = order.payment
        if payment.status == Payment.STATUS_SUCCEEDED:
            raise ValidationError("Order has already been successfully paid.")
            
        if payment.amount != order.total_price or payment.currency != currency:
            raise ValidationError("Existing payment intent amount mismatch. Cannot safely reuse.")
            
        try:
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
            if intent.status == 'succeeded':
                payment.status = Payment.STATUS_SUCCEEDED
                payment.save(update_fields=['status', 'updated_at'])
                raise ValidationError("Order has already been successfully paid.")
            return intent.client_secret
        except stripe.error.StripeError as e:
            raise ValidationError(f"Stripe error retrieving intent: {str(e)}")

    # 3. Create New PaymentIntent idempotently
    idempotency_key = f"payment_intent_order_{order.id}"
    stripe_amount = convert_to_stripe_amount(order.total_price)
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=stripe_amount,
            currency=currency,
            metadata={'order_id': str(order.id)},
            idempotency_key=idempotency_key
        )
        
        try:
            Payment.objects.create(
                order=order,
                stripe_payment_intent_id=intent.id,
                amount=order.total_price,
                currency=currency,
                status=Payment.STATUS_PENDING
            )
        except Exception:
            # If another thread created the payment record concurrently, safely reuse it
            existing = Payment.objects.filter(order=order).first()
            if not existing:
                raise
        
        return intent.client_secret
    except stripe.error.StripeError as e:
        raise ValidationError(f"Failed to create Stripe PaymentIntent: {str(e)}")
        raise ValidationError(f"Failed to create Stripe PaymentIntent: {str(e)}")
