from collections import Counter
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from restaurants.catalog.rivne import RIVNE_CATALOG
from restaurants.catalog.validation import CatalogValidationError, validate_catalog
from restaurants.models import Category, Cuisine, MenuItem, MenuTag, OpeningHours, Restaurant


class Command(BaseCommand):
    help = "Create or update the validated Rivne catalog without deleting transactional data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and simulate the catalog import without committing changes.",
        )

    def handle(self, *args, **options):
        try:
            validate_catalog(RIVNE_CATALOG)
        except CatalogValidationError as error:
            raise CommandError(str(error)) from error

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS("Dry run complete"))
            self.stdout.write(
                f"validated_restaurants={len(RIVNE_CATALOG)} "
                f"validated_menu_items={sum(len(record.get('menu_items', ())) for record in RIVNE_CATALOG)}"
            )
            return

        summary = Counter()
        with transaction.atomic():
            for record in RIVNE_CATALOG:
                cuisine, cuisine_created = Cuisine.objects.get_or_create(
                    name=record["cuisine"]
                )
                summary["cuisines_created"] += int(cuisine_created)

                restaurant = Restaurant.objects.filter(
                    catalog_key=record["catalog_key"]
                ).first()
                is_created = restaurant is None
                if restaurant is None:
                    restaurant = Restaurant(catalog_key=record["catalog_key"])

                restaurant.name = record["name"]
                restaurant.description = record["description"]
                restaurant.address = record["address"]
                restaurant.latitude = Decimal(record["latitude"])
                restaurant.longitude = Decimal(record["longitude"])
                restaurant.cuisine = cuisine
                restaurant.rating = record["rating"]
                restaurant.review_count = record["review_count"]
                restaurant.delivery_time = record["delivery_time"]
                restaurant.image_url = record.get("image_url", "")
                restaurant.is_active = True
                restaurant.full_clean()
                restaurant.save()
                summary["restaurants_created" if is_created else "restaurants_updated"] += 1

                for day_type, (opens_at, closes_at) in record["opening_hours"].items():
                    _, hours_created = OpeningHours.objects.update_or_create(
                        restaurant=restaurant,
                        day_type=day_type,
                        defaults={"opens_at": opens_at, "closes_at": closes_at},
                    )
                    summary["hours_created" if hours_created else "hours_updated"] += 1

                for item_data in record.get("menu_items", ()):
                    category, category_created = Category.objects.get_or_create(
                        name=item_data["category"]
                    )
                    summary["categories_created"] += int(category_created)
                    item = MenuItem.objects.filter(
                        restaurant=restaurant,
                        name=item_data["name"],
                    ).first()
                    item_created = item is None
                    if item is None:
                        item = MenuItem(restaurant=restaurant, name=item_data["name"])

                    item.category = category
                    item.description = item_data.get("description", "")
                    item.price = Decimal(item_data["price"])
                    item.image_url = item_data.get("image_url", "")
                    item.is_available = item_data.get("is_available", True)
                    item.unavailable_reason = item_data.get("unavailable_reason", "")
                    item.is_vegetarian = item_data.get("is_vegetarian", False)
                    item.is_vegan = item_data.get("is_vegan", False)
                    item.calories = item_data.get("calories")
                    item.full_clean()
                    item.save()
                    tags = []
                    for tag_name in item_data.get("tags", ()):
                        tag, _ = MenuTag.objects.get_or_create(name=tag_name)
                        tags.append(tag)
                    item.tags.set(tags)
                    summary["items_created" if item_created else "items_updated"] += 1

        self.stdout.write(self.style.SUCCESS("Catalog import complete"))
        self.stdout.write(
            " ".join(
                f"{key}={summary[key]}" for key in sorted(summary)
            ) or "No records changed."
        )