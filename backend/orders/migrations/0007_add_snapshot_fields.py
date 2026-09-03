from django.db import migrations, models


def populate_snapshots(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    OrderItem = apps.get_model('orders', 'OrderItem')

    for order in Order.objects.select_related('restaurant'):
        order.restaurant_name_snapshot = order.restaurant.name
        order.save(update_fields=['restaurant_name_snapshot'])

    for item in OrderItem.objects.select_related('menu_item__restaurant'):
        item.menu_item_name_snapshot = item.menu_item.name
        item.restaurant_name_snapshot = item.menu_item.restaurant.name
        item.save(update_fields=[
            'menu_item_name_snapshot',
            'restaurant_name_snapshot',
        ])


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
        migrations.RunPython(populate_snapshots, migrations.RunPython.noop),
    ]
