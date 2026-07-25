import django.db.models.deletion
from django.db import migrations, models
from django.utils import timezone


def assign_default_cuisine_and_merge_categories(apps, schema_editor):
    Cuisine = apps.get_model("restaurants", "Cuisine")
    Restaurant = apps.get_model("restaurants", "Restaurant")
    Category = apps.get_model("restaurants", "Category")
    MenuItem = apps.get_model("restaurants", "MenuItem")

    default_cuisine, _ = Cuisine.objects.get_or_create(name="Unassigned")
    Restaurant.objects.filter(cuisine__isnull=True).update(cuisine=default_cuisine)

    seen_categories = {}
    for category in Category.objects.order_by("id"):
        existing_category_id = seen_categories.get(category.name)
        if existing_category_id is None:
            seen_categories[category.name] = category.id
            continue

        MenuItem.objects.filter(category_id=category.id).update(category_id=existing_category_id)
        category.delete()


def remove_default_cuisine(apps, schema_editor):
    Cuisine = apps.get_model("restaurants", "Cuisine")
    Cuisine.objects.filter(name="Unassigned").delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("restaurants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cuisine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="restaurant",
            name="address",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="created_at",
            field=models.DateTimeField(default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="restaurant",
            name="cuisine",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="restaurants", to="restaurants.cuisine"),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="delivery_time",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="image_url",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="rating",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="image_url",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="is_available",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="menuitem",
            name="category",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="menu_items", to="restaurants.category"),
        ),
        migrations.RunPython(assign_default_cuisine_and_merge_categories, remove_default_cuisine),
        migrations.RemoveField(
            model_name="category",
            name="restaurant",
        ),
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="restaurant",
            name="cuisine",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="restaurants", to="restaurants.cuisine"),
        ),
    ]
