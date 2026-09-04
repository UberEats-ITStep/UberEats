from django.db import migrations, models


def populate_snapshots(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    OrderItem = apps.get_model('orders', 'OrderItem')
    MenuItem = apps.get_model('restaurants', 'MenuItem')
    Restaurant = apps.get_model('restaurants', 'Restaurant')

    for order in Order.objects.all():
        if not order.restaurant_name_snapshot and order.restaurant_id:
            try:
                rest = Restaurant.objects.get(pk=order.restaurant_id)
                order.restaurant_name_snapshot = rest.name
                order.save(update_fields=['restaurant_name_snapshot'])
            except Restaurant.DoesNotExist:
                # leave as default empty string
                continue

    for oi in OrderItem.objects.all():
        updated = False
        if not oi.menu_item_name_snapshot and oi.menu_item_id:
            try:
                mi = MenuItem.objects.get(pk=oi.menu_item_id)
                oi.menu_item_name_snapshot = mi.name
                updated = True
                try:
                    oi.restaurant_name_snapshot = mi.restaurant.name
                except Exception:
                    oi.restaurant_name_snapshot = ''
            except MenuItem.DoesNotExist:
                # try to fall back to order-level restaurant snapshot
                if getattr(oi, 'order_id', None):
                    try:
                        order = Order.objects.get(pk=oi.order_id)
                        oi.restaurant_name_snapshot = getattr(order, 'restaurant_name_snapshot', '') or ''
                        updated = True
                    except Order.DoesNotExist:
                        pass
        if updated:
            oi.save(update_fields=['menu_item_name_snapshot', 'restaurant_name_snapshot'])


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_order_delivery_coordinates_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant_name_snapshot',
            field=models.CharField(max_length=255, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='menu_item_name_snapshot',
            field=models.CharField(max_length=255, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='restaurant_name_snapshot',
            field=models.CharField(max_length=255, blank=True, default=''),
        ),
        migrations.RunPython(populate_snapshots, reverse_code=migrations.RunPython.noop),
    ]
