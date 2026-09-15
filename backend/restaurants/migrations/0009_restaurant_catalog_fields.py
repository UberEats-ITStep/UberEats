from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("restaurants", "0008_menutag_menuitem_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="catalog_key",
            field=models.SlugField(blank=True, editable=False, max_length=80, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]