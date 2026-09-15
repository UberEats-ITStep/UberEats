"""Give duplicated restaurant records distinct Cloudinary cover assets."""

from __future__ import annotations

from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from restaurants.models import MenuItem, Restaurant


# These records inherited the brewery cover during the earlier catalog-wide
# fallback. Use each restaurant's own existing catalog media, without touching
# any menu-item field.
REPLACEMENT_MENU_ITEMS = {
    9: 137,   # Lunch — Banosh with Brynza
    14: 218,  # Pan Khaliavskyi — Chicken Kyiv
    25: 391,  # Levada — Deruny
    26: 408,  # Melange — Deruny with Mushroom Sauce
    28: 443,  # Tradition — Holubtsi
}
BRANDED_RESTAURANT_SOURCES = {
    34: "https://upload.wikimedia.org/wikipedia/commons/7/76/Interior%2C_McDonald%27s_restaurant_in_Rose_Hill%2C_Virginia.jpg",
    35: "https://upload.wikimedia.org/wikipedia/commons/0/0f/Interior_McDonald%27s_Restaurant_downtown_Saint_Johnsbury_September_2017.jpg",
    36: "https://upload.wikimedia.org/wikipedia/commons/3/35/GD_%E5%BB%A3%E6%9D%B1_Guangdong_%E5%BB%A3%E5%B7%9E_Guangzhou_%E8%8A%B1%E5%9F%8E%E5%A4%A7%E9%81%93_HuaCheng_Avenue_%E8%8F%AF%E7%A9%97%E8%B7%AF_HuaSui_Road_shop_KFC_Restaurant_interior_slogan_sign_September_2024_R12S.jpg",
}
USER_AGENT = "BiteUp-restaurant-media-deduplication/1.0"


class Command(BaseCommand):
    help = "Replace duplicated restaurant covers with distinct existing catalog media."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report planned replacements without uploading or changing records.",
        )

    def handle(self, *args, **options):
        planned = []
        for restaurant_id, menu_item_id in REPLACEMENT_MENU_ITEMS.items():
            restaurant = Restaurant.objects.get(id=restaurant_id)
            item = MenuItem.objects.select_related("restaurant").get(id=menu_item_id)
            if item.restaurant_id != restaurant.id:
                raise CommandError(
                    f"Menu item {item.id} does not belong to restaurant {restaurant.id}."
                )
            if not item.image:
                raise CommandError(f"Menu item {item.id} has no source image.")
            planned.append((restaurant, item))
        branded = [
            (Restaurant.objects.get(id=restaurant_id), source_url)
            for restaurant_id, source_url in BRANDED_RESTAURANT_SOURCES.items()
        ]

        if options["dry_run"]:
            for restaurant, item in planned:
                self.stdout.write(
                    f"{restaurant.id}: {restaurant.name} <- menu {item.id}: {item.name}"
                )
            for restaurant, source_url in branded:
                self.stdout.write(f"{restaurant.id}: {restaurant.name} <- {source_url}")
            return

        for restaurant, item in planned:
            request = Request(item.image.url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=30) as response:
                payload = response.read()
            filename = f"cover-{restaurant.catalog_key}.jpg"
            with transaction.atomic():
                restaurant.image.save(filename, ContentFile(payload), save=False)
                restaurant.save(update_fields=["image"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Uploaded restaurant {restaurant.id}: {restaurant.image.name}"
                )
            )
        for restaurant, source_url in branded:
            request = Request(source_url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=60) as response:
                payload = response.read()
            with transaction.atomic():
                restaurant.image.save(
                    f"cover-{restaurant.catalog_key}.jpg",
                    ContentFile(payload),
                    save=False,
                )
                restaurant.save(update_fields=["image"])
            self.stdout.write(
                self.style.SUCCESS(
                    f"Uploaded branded restaurant {restaurant.id}: {restaurant.image.name}"
                )
            )
