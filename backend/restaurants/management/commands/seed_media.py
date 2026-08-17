"""
Idempotent dev-data seeding for restaurant/menu-item media.

Usage:
    python manage.py seed_media

Safe to run repeatedly: every restaurant/menu item is keyed by name via
`update_or_create`, so re-running updates existing rows in place instead of
duplicating them, and only touches `image_url` (never clobbers a real
uploaded `image`).

Images point at picsum.photos with a fixed seed per item, which:
  - always resolves to a real, stable image (no 404s / broken links)
  - is deterministic (same seed -> same picture every run)
  - needs no local file storage, so seeding stays fast and dependency-free
Swap `_image_url()` for real asset URLs (or S3/Cloudinary keys) once actual
photography exists — nothing else in the seed script needs to change.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from restaurants.models import Category, Cuisine, MenuItem, Restaurant

RESTAURANTS = [
    {"name": "Sakura Sushi", "cuisine": "Japanese", "rating": "4.70", "delivery_time": 35,
     "address": "12 Khreshchatyk St, Kyiv"},
    {"name": "Pizzeria Bella", "cuisine": "Italian", "rating": "4.50", "delivery_time": 25,
     "address": "5 Velyka Vasylkivska St, Kyiv"},
    {"name": "Burger Barn", "cuisine": "American", "rating": "4.30", "delivery_time": 20,
     "address": "8 Antonovycha St, Kyiv"},
    {"name": "Taco Fiesta", "cuisine": "Mexican", "rating": "4.60", "delivery_time": 30,
     "address": "22 Sichovykh Striltsiv St, Kyiv"},
]

MENU_ITEMS = {
    "Sakura Sushi": [
        ("Rolls", "Spicy Tuna Roll", "12.50"),
        ("Rolls", "Salmon Nigiri", "9.90"),
        ("Drinks", "Green Tea", "3.50"),
    ],
    "Pizzeria Bella": [
        ("Mains", "Margherita Pizza", "199.00"),
        ("Mains", "Quattro Formaggi", "229.00"),
        ("Drinks", "Cola", "39.00"),
    ],
    "Burger Barn": [
        ("Mains", "Classic Cheeseburger", "159.00"),
        ("Sides", "Fries", "59.00"),
    ],
    "Taco Fiesta": [
        ("Mains", "Al Pastor Tacos (3pc)", "119.00"),
        ("Mains", "Veggie Burrito", "99.00"),
    ],
}


def _image_url(seed: str, width: int, height: int) -> str:
    return f"https://picsum.photos/seed/{slugify(seed)}/{width}/{height}"


class Command(BaseCommand):
    help = "Seed restaurants and menu items with realistic, non-broken placeholder images."

    @transaction.atomic
    def handle(self, *args, **options):
        created_restaurants = 0
        created_items = 0

        for entry in RESTAURANTS:
            cuisine, _ = Cuisine.objects.get_or_create(name=entry["cuisine"])
            restaurant, was_created = Restaurant.objects.update_or_create(
                name=entry["name"],
                defaults={
                    "description": f"Popular {entry['cuisine']} spot in Kyiv.",
                    "address": entry["address"],
                    "cuisine": cuisine,
                    "rating": entry["rating"],
                    "delivery_time": entry["delivery_time"],
                    # Only seed image_url if there's no real upload already.
                    **({"image_url": _image_url(entry["name"], 800, 500)}),
                },
            )
            created_restaurants += int(was_created)

            for category_name, item_name, price in MENU_ITEMS.get(entry["name"], []):
                category, _ = Category.objects.get_or_create(name=category_name)
                _, item_created = MenuItem.objects.update_or_create(
                    restaurant=restaurant,
                    slug=slugify(item_name),
                    defaults={
                        "category": category,
                        "name": item_name,
                        "description": f"{item_name} from {entry['name']}.",
                        "price": price,
                        "image_url": _image_url(f"{entry['name']}-{item_name}", 400, 300),
                        "is_available": True,
                    },
                )
                created_items += int(item_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_restaurants} restaurants, "
                f"{created_items} menu items created/updated."
            )
        )