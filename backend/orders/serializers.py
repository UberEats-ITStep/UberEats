from django.db import transaction
from rest_framework import serializers

from restaurants.models import MenuItem

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'delivery_address', 'created_at', 'items', 'restaurant', 'courier']


class CheckoutSerializer(serializers.Serializer):
    delivery_address = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        user = self.context['request'].user
        
        if not hasattr(user, 'cart') or not user.cart.items.exists():
            raise serializers.ValidationError({'non_field_errors': 'Your cart is empty.'})
            
        items = user.cart.items.select_related('menu_item')
        restaurant_ids = {item.menu_item.restaurant_id for item in items}
        if len(restaurant_ids) > 1:
            raise serializers.ValidationError({'non_field_errors': 'All items must belong to the same restaurant.'})
            
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        cart = user.cart
        cart_items = cart.items.select_related('menu_item').all()
        
        restaurant = cart_items[0].menu_item.restaurant
        
        order = Order.objects.create(
            client=user,
            restaurant=restaurant,
            delivery_address=validated_data.get('delivery_address', ''),
        )

        total_price = 0
        order_items_to_create = []
        for item in cart_items:
            total_price += item.menu_item.price * item.quantity
            order_items_to_create.append(
                OrderItem(
                    order=order,
                    menu_item=item.menu_item,
                    quantity=item.quantity,
                    price=item.menu_item.price,
                )
            )

        OrderItem.objects.bulk_create(order_items_to_create)
        
        order.total_price = total_price
        order.save()
        
        cart.items.all().delete()
        
        return order


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status']