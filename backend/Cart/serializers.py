from rest_framework import serializers

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = CartItem
        fields = "__all__"

    def validate(self, attrs):

        cart = attrs["cart"]
        menu_item = attrs["menu_item"]

        items = cart.items.all()

        if items.exists():

            restaurant = items.first().menu_item.restaurant

            if menu_item.restaurant != restaurant:
                raise serializers.ValidationError(
                    "Cart can contain items from only one restaurant."
                )

        return attrs


class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"