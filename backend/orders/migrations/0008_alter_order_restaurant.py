from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0007_add_snapshot_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="restaurant",
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name="orders",
                to="restaurants.restaurant",
            ),
        ),
    ]