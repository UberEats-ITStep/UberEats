from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsAdminOrAuthenticatedReadOnly, is_admin

from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer, OrderStatusSerializer


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(client=self.request.user)
            .exclude(status=Order.STATUS_DECLINED)
            .select_related('restaurant')
            .prefetch_related('items__menu_item')
            .order_by('-created_at')
        )


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return (
            Order.objects.filter(client=self.request.user)
            .select_related('restaurant')
            .prefetch_related('items__menu_item')
        )


class OrderStatusView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminOrAuthenticatedReadOnly]
    serializer_class = OrderStatusSerializer

    def get_queryset(self):
        if is_admin(self.request.user):
            return Order.objects.all()
        return Order.objects.filter(client=self.request.user)