from django.urls import path

from .views import CheckoutView, OrderHistoryView, OrderStatusView


urlpatterns = [
    path('orders/checkout/', CheckoutView.as_view(), name='order_checkout'),
    path('orders/history/', OrderHistoryView.as_view(), name='order_history'),
    path('orders/<int:pk>/status/', OrderStatusView.as_view(), name='order_status'),
]