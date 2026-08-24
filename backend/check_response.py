import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import Order
from orders.serializers import OrderSerializer
from restaurants.models import Restaurant, Cuisine
from users.models import User
from decimal import Decimal

# Create a mock order just to serialize it
user = User.objects.first()
if not user:
    user = User.objects.create(email="test@test.com", username="testuser")

cuisine, _ = Cuisine.objects.get_or_create(name="Italian")
restaurant, _ = Restaurant.objects.get_or_create(
    name="Test Rest", 
    cuisine=cuisine, 
    defaults={"latitude": Decimal("50.615"), "longitude": Decimal("26.26")}
)

order = Order.objects.create(
    client=user,
    restaurant=restaurant,
    status="DELIVERING",
    delivery_latitude=Decimal("50.62"),
    delivery_longitude=Decimal("26.25"),
    delivery_address="Rivne, Tsentr"
)

serializer = OrderSerializer(order)
print(json.dumps(serializer.data, indent=2))

order.delete()
