from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related("restaurant").prefetch_related("items__menu_item")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related("menu_item")

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        cart_field = getattr(serializer, "fields", {}).get("cart")
        if (
            cart_field is not None
            and not cart_field.read_only
            and hasattr(cart_field, "queryset")
        ):
            cart_field.queryset = Cart.objects.filter(user=self.request.user)
        return serializer

    def _assert_cart_is_own(self, serializer):
        cart = serializer.validated_data.get("cart")
        if cart is not None and cart.user_id != self.request.user.pk:
            raise PermissionDenied("You do not have permission to use this cart.")

    def perform_create(self, serializer):
        self._assert_cart_is_own(serializer)
        serializer.save()

    def perform_update(self, serializer):
        self._assert_cart_is_own(serializer)
        serializer.save()