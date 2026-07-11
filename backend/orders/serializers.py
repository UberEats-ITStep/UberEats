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
        fields = ['id', 'status', 'total_price', 'delivery_address', 'created_at', 'items']


class OrderHistoryItemSerializer(serializers.ModelSerializer):
    menuItemId = serializers.IntegerField(source='menu_item_id', read_only=True)
    name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuItemId', 'name', 'quantity', 'price']


class OrderHistorySerializer(serializers.ModelSerializer):
    restaurantName = serializers.SerializerMethodField()
    totalPrice = serializers.DecimalField(
        source='total_price',
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    itemCount = serializers.SerializerMethodField()
    items = OrderHistoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'restaurantName',
            'status',
            'totalPrice',
            'createdAt',
            'itemCount',
            'items',
        ]

    def get_restaurantName(self, order):
        first_item = next(iter(order.items.all()), None)
        return first_item.menu_item.restaurant.name if first_item else None

    def get_itemCount(self, order):
        return sum(item.quantity for item in order.items.all())


class CheckoutItemSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class CheckoutSerializer(serializers.Serializer):
    items = CheckoutItemSerializer(many=True)
    delivery_address = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Order must contain at least one item.')
        return value

    def create(self, validated_data):
        order = Order.objects.create(
            user=self.context['request'].user,
            delivery_address=validated_data.get('delivery_address', ''),
        )

        total_price = 0
        for item in validated_data['items']:
            menu_item = item['menu_item']
            quantity = item['quantity']

            total_price += menu_item.price * quantity
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity,
                price=menu_item.price,
            )

        order.total_price = total_price
        order.save()
        return order


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status']