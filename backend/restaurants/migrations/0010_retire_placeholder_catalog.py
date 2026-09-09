from django.db import migrations


def retire_placeholder_catalog_records(apps, schema_editor):
    Restaurant = apps.get_model("restaurants", "Restaurant")
    Restaurant.objects.filter(image_url__icontains="picsum.photos").update(
        is_active=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ("restaurants", "0009_restaurant_catalog_fields"),
    ]

    operations = [
        migrations.RunPython(
            retire_placeholder_catalog_records,
            reverse_code=migrations.RunPython.noop,
        ),
    ]