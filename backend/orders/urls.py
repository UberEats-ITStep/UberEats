from django.urls import path

from .views import CheckoutView, OrderDetailView, OrderHistoryView, OrderStatusView


urlpatterns = [
    path('orders/checkout/', CheckoutView.as_view(), name='order_checkout'),
    path('orders/history/', OrderHistoryView.as_view(), name='order_history'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/status/', OrderStatusView.as_view(), name='order_status'),
]
