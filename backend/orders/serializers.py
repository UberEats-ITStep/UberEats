from django.db import transaction
from rest_framework import serializers

from restaurants.models import MenuItem
from users.models import DeliveryAddress

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price', 'subtotal']

    def get_subtotal(self, obj):
        return f'{obj.price * obj.quantity:.2f}'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'total_price',
            'street',
            'building',
            'apartment',
            'entrance',
            'floor',
            'delivery_notes',
            'contact_phone',
            'delivery_latitude',
            'delivery_longitude',
            'created_at',
            'items',
            'restaurant',
            'restaurant_name',
            'courier',
        ]


class CheckoutSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField(
        required=False,
        write_only=True,
        min_value=1,
    )
    street = serializers.CharField(max_length=255, required=False)
    building = serializers.CharField(max_length=20, required=False)

    apartment = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )
    entrance = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )
    floor = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=100,
    )
    delivery_notes = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
    )
    contact_phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    def validate_street(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Street cannot be empty.'
            )

        return value

    def validate_building(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Building cannot be empty.'
            )

        return value

    def validate_contact_phone(self, value):
        value = value.strip()

        if value:
            import re

            if not re.fullmatch(r'^\+?[0-9\s\-()]{7,20}$', value):
                raise serializers.ValidationError(
                    'Enter a valid phone number.'
                )

        return value

    def validate(self, attrs):
        user = self.context['request'].user
        delivery_address_id = attrs.get('delivery_address_id')

        manual_address_fields = {
            'street',
            'building',
            'apartment',
            'entrance',
            'floor',
            'delivery_notes',
            'contact_phone',
        }

        if delivery_address_id is not None:
            provided_manual_fields = manual_address_fields.intersection(attrs)
            if provided_manual_fields:
                raise serializers.ValidationError({
                    'non_field_errors': (
                        'Provide either delivery_address_id or manual delivery fields, not both.'
                    )
                })

            delivery_address = DeliveryAddress.objects.filter(
                pk=delivery_address_id,
                user=user,
            ).first()
            if delivery_address is None:
                raise serializers.ValidationError({
                    'delivery_address_id': 'Delivery address not found.'
                })
            if not delivery_address.street or not delivery_address.building:
                raise serializers.ValidationError({
                    'delivery_address_id': (
                        'This delivery address must be confirmed before checkout.'
                    )
                })

            attrs['delivery_address'] = delivery_address
        else:
            missing_fields = {
                field: 'This field is required.'
                for field in ('street', 'building')
                if field not in attrs
            }
            if missing_fields:
                raise serializers.ValidationError(missing_fields)

        if not hasattr(user, 'cart') or not user.cart.items.exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Your cart is empty.'
            })

        items = user.cart.items.select_related('menu_item')

        restaurant_ids = {
            item.menu_item.restaurant_id
            for item in items
        }

        if len(restaurant_ids) > 1:
            raise serializers.ValidationError({
                'non_field_errors':
                    'All items must belong to the same restaurant.'
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        cart = user.cart
        delivery_address = validated_data.pop('delivery_address', None)
        validated_data.pop('delivery_address_id', None)

        cart_items = cart.items.select_related(
            'menu_item'
        ).all()

        restaurant = cart_items[0].menu_item.restaurant

        if delivery_address is not None:
            order = Order.objects.create(
                client=user,
                restaurant=restaurant,
                street=delivery_address.street,
                building=delivery_address.building,
                apartment=delivery_address.apartment,
                entrance=delivery_address.entrance,
                floor=delivery_address.floor,
                delivery_notes=delivery_address.delivery_notes,
                contact_phone=delivery_address.contact_phone,
                delivery_latitude=delivery_address.latitude,
                delivery_longitude=delivery_address.longitude,
            )
        else:
            order = Order.objects.create(
                client=user,
                restaurant=restaurant,
                street=validated_data['street'],
                building=validated_data['building'],
                apartment=validated_data.get('apartment', ''),
                entrance=validated_data.get('entrance', ''),
                floor=validated_data.get('floor'),
                delivery_notes=validated_data.get('delivery_notes', ''),
                contact_phone=validated_data.get('contact_phone', ''),
            )

        total_price = 0
        order_items_to_create = []

        for item in cart_items:
            total_price += (
                item.menu_item.price * item.quantity
            )

            order_items_to_create.append(
                OrderItem(
                    order=order,
                    menu_item=item.menu_item,
                    quantity=item.quantity,
                    price=item.menu_item.price,
                )
            )

        OrderItem.objects.bulk_create(
            order_items_to_create
        )

        order.total_price = total_price
        order.save(
            update_fields=['total_price']
        )

        cart.items.all().delete()

        return order

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status']