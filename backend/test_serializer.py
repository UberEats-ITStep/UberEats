import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from orders.models import Order
from orders.serializers import OrderSerializer
import json

orders = Order.objects.all()[:1]
if orders.exists():
    data = OrderSerializer(orders[0]).data
    print(json.dumps(data, indent=2))
else:
    print("No orders found")
