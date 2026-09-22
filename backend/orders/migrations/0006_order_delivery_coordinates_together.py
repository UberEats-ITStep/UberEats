from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0005_merge_20260827_1110'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='order',
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        delivery_latitude__isnull=True,
                        delivery_longitude__isnull=True,
                    )
                    | models.Q(
                        delivery_latitude__isnull=False,
                        delivery_longitude__isnull=False,
                    )
                ),
                name='order_delivery_coordinates_together',
            ),
        ),
    ]
