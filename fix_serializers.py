import sys
import re

filepath = 'backend/orders/serializers.py'
with open(filepath, 'r') as f:
    content = f.read()

# Block 1: OrderSerializer.Meta.fields
merged_fields = """            'id',
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
            'courier',"""

# Need to precisely replace the first conflict block
content = re.sub(
    r'<<<<<<< HEAD\n\s*\'id\', \'status\'.*?\n=======\n(.*?)\n>>>>>>> dev',
    merged_fields,
    content,
    flags=re.DOTALL,
    count=1
)

# Block 2: CheckoutSerializer fields
merged_checkout_fields = """    street = serializers.CharField(max_length=255)
    building = serializers.CharField(max_length=20)
    
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

            if not re.fullmatch(r'^\\+?[0-9\\s\\-()]{7,20}$', value):
                raise serializers.ValidationError(
                    'Enter a valid phone number.'
                )

        return value"""

content = re.sub(
    r'<<<<<<< HEAD\n.*?delivery_longitude.*?=======\n.*?\n>>>>>>> dev',
    merged_checkout_fields.replace('\\', '\\\\'),
    content,
    flags=re.DOTALL,
    count=1
)

# Block 3: Order.objects.create
merged_create = """            street=validated_data['street'],
            building=validated_data['building'],
            apartment=validated_data.get('apartment', ''),
            entrance=validated_data.get('entrance', ''),
            floor=validated_data.get('floor'),
            delivery_notes=validated_data.get('delivery_notes', ''),
            contact_phone=validated_data.get('contact_phone', ''),
            delivery_latitude=validated_data.get('delivery_latitude'),
            delivery_longitude=validated_data.get('delivery_longitude'),"""

content = re.sub(
    r'<<<<<<< HEAD\n.*?delivery_longitude.*?=======\n(.*?)\n>>>>>>> dev',
    merged_create,
    content,
    flags=re.DOTALL,
    count=1
)

with open(filepath, 'w') as f:
    f.write(content)
