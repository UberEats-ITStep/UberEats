import json
import os

import django


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from orders.models import Order
    from orders.serializers import OrderSerializer

    order = Order.objects.first()
    if order:
        print(json.dumps(OrderSerializer(order).data, indent=2))
    else:
        print("No orders found")


if __name__ == "__main__":
    main()
