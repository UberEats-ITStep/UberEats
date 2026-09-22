from django.urls import path
from .views import CreatePaymentIntentView, StripeWebhookView, PaymentFailedView

urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create-intent'),
    path('payment-failed/', PaymentFailedView.as_view(), name='payment-failed'),
    path('webhook/', StripeWebhookView.as_view(), name='webhook'),
]
