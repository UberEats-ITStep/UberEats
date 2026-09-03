from decimal import Decimal
from django.db import transaction
from rest_framework import serializers

from cart.models import Cart
from restaurants.models import MenuItem
from users.models import DeliveryAddress

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price', 'subtotal']

    def get_subtotal(self, obj):
        return f'{obj.price * obj.quantity:.2f}'

    def get_menu_item_name(self, obj):
        return obj.menu_item_name_snapshot or obj.menu_item.name


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.SerializerMethodField()
    restaurant_latitude = serializers.DecimalField(source='restaurant.latitude', max_digits=9, decimal_places=6, read_only=True)
    restaurant_longitude = serializers.DecimalField(source='restaurant.longitude', max_digits=9, decimal_places=6, read_only=True)
    review_id = serializers.SerializerMethodField()

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
            'restaurant_latitude',
            'restaurant_longitude',
            'courier',
            'review_id',
        ]

    def get_review_id(self, obj):
        review = getattr(obj, 'review', None)
        return review.id if review else None

    def get_restaurant_name(self, obj):
        return obj.restaurant_name_snapshot or obj.restaurant.name


class CheckoutSerializer(serializers.Serializer):
    delivery_address_id = serializers.IntegerField(
        required=False,
        write_only=True,
        min_value=1,
    )
    street = serializers.CharField(max_length=255, required=False)
    building = serializers.CharField(max_length=20, required=False)
    delivery_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    delivery_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

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
            raise serializers.ValidationError('Street cannot be empty.')
        return value

    def validate_building(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Building cannot be empty.')
        return value

    def validate_contact_phone(self, value):
        value = value.strip()
        if value:
            import re
            if not re.fullmatch(r'^\+?[0-9\s\-()]{7,20}$', value):
                raise serializers.ValidationError('Enter a valid phone number.')
        return value

    def validate(self, attrs):
        lat = attrs.get('delivery_latitude')
        lng = attrs.get('delivery_longitude')
        if (lat is None) != (lng is None):
            missing_field = 'delivery_longitude' if lng is None else 'delivery_latitude'
            raise serializers.ValidationError({
                missing_field: 'Delivery latitude and longitude must both be set, or both be empty.'
            })

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
            'delivery_latitude',
            'delivery_longitude',
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

        # Ensure cart exists
        cart = getattr(user, 'cart', None)
        if cart is None:
            cart, _ = Cart.objects.get_or_create(user=user)

        delivery_address = validated_data.pop('delivery_address', None)
        validated_data.pop('delivery_address_id', None)

        cart_items = list(cart.items.select_related('menu_item').all())

        # Determine restaurant from cart items (validated to be single restaurant)
        restaurant = None
        if cart_items:
            restaurant = cart_items[0].menu_item.restaurant

        # Snapshot delivery details
        if delivery_address:
            street = delivery_address.street
            building = delivery_address.building
            apartment = delivery_address.apartment
            entrance = delivery_address.entrance
            floor = delivery_address.floor
            delivery_notes = delivery_address.delivery_notes
            contact_phone = delivery_address.contact_phone
            delivery_latitude = delivery_address.latitude
            delivery_longitude = delivery_address.longitude
        else:
            street = validated_data.get('street', '')
            building = validated_data.get('building', '')
            apartment = validated_data.get('apartment', '')
            entrance = validated_data.get('entrance', '')
            floor = validated_data.get('floor', None)
            delivery_notes = validated_data.get('delivery_notes', '')
            contact_phone = validated_data.get('contact_phone', '')
            delivery_latitude = validated_data.get('delivery_latitude', None)
            delivery_longitude = validated_data.get('delivery_longitude', None)

        # Calculate total price using Decimal
        total_price = Decimal('0.00')
        for item in cart_items:
            price = Decimal(str(item.menu_item.price))
            total_price += price * item.quantity

        order = Order.objects.create(
            client=user,
            restaurant=restaurant,
            total_price=total_price,
            street=street,
            building=building,
            apartment=apartment or '',
            entrance=entrance or '',
            floor=floor,
            delivery_notes=delivery_notes or '',
            contact_phone=contact_phone or '',
            delivery_latitude=delivery_latitude,
            delivery_longitude=delivery_longitude,
            restaurant_name_snapshot=restaurant.name,
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                price=item.menu_item.price,
                menu_item_name_snapshot=item.menu_item.name,
                restaurant_name_snapshot=restaurant.name,
            )

        # Clear cart
        cart.items.all().delete()

        return order


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'status']

    def validate_status(self, value):
        valid_statuses = {s[0] for s in Order.STATUS_CHOICES}
        if value not in valid_statuses:
            raise serializers.ValidationError('Invalid order status.')
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
