from rest_framework import serializers

from .models import Cart, CartItem
from restaurants.models import MenuItem


class SimpleMenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    menu_item_detail = SimpleMenuItemSerializer(source="menu_item", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "cart", "menu_item", "quantity", "menu_item_detail"]
        # Remove UniqueTogetherValidator to allow custom aggregation logic in create()
        validators = []

    def validate_cart(self, value):
        request = self.context.get("request")
        if request and value.user != request.user:
            raise serializers.ValidationError("You do not have permission to modify this cart.")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, attrs):
        cart = attrs.get("cart", self.instance.cart if self.instance else None)
        menu_item = attrs.get("menu_item", self.instance.menu_item if self.instance else None)

        if cart and menu_item:
            if cart.restaurant and menu_item.restaurant != cart.restaurant:
                raise serializers.ValidationError(
                    "Cart can contain items from only one restaurant."
                )
        return attrs

    def create(self, validated_data):
        cart = validated_data["cart"]
        menu_item = validated_data["menu_item"]
        quantity = validated_data.get("quantity", 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        if not cart.restaurant:
            cart.restaurant = menu_item.restaurant
            cart.save()

        return item


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ['user']