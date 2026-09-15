"""Refresh restaurant covers from stable, already-uploaded catalog food media."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from restaurants.models import MenuItem, Restaurant


KEYWORDS = {
    "Bakery": ("croissant", "cake", "bread", "pastry"),
    "Cafe": ("coffee", "cappuccino", "latte", "cake", "dessert"),
    "European": ("steak", "salmon", "chicken", "vegetables"),
    "Fast Food": ("big mac", "mcnugget", "fries", "bucket", "zinger", "burger"),
    "Georgian": ("khachapuri", "khinkali", "mtsvadi", "chakhokhbili"),
    "Italian": ("pizza", "pasta", "lasagna", "bruschetta"),
    "Japanese": ("sushi", "sashimi", "ramen"),
    "Pub": ("burger", "ribs", "sausages", "nachos", "onion rings"),
    "Ukrainian": ("varenyky", "deruny", "holubtsi", "borscht", "banosh"),
}


def download(url: str) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "BiteUp-restaurant-cover-refresh/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    if len(data) < 10_000:
        raise ValueError("downloaded image is unexpectedly small")
    return data


class Command(BaseCommand):
    help = "Give every restaurant a distinct cuisine-matched Cloudinary cover."

    def add_arguments(self, parser):
        parser.add_argument("--backup", default="/tmp/biteup-media-backup/restaurant-image-urls.json")
        parser.add_argument("--manifest", default="docs/catalog-image-manifest.md")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--ids", nargs="*", type=int)

    def handle(self, *args, **options):
        queryset = Restaurant.objects.select_related("cuisine").order_by("id")
        if options["ids"]:
            queryset = queryset.filter(id__in=options["ids"])
        restaurants = list(queryset)
        menu_items = list(MenuItem.objects.exclude(image="").select_related("restaurant"))
        before = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "image": restaurant.image.name if restaurant.image else "",
                "image_url": restaurant.resolved_image_url,
            }
            for restaurant in restaurants
        ]
        backup = Path(options["backup"])
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(json.dumps(before, ensure_ascii=False, indent=2), encoding="utf-8")

        used_sources: set[str] = set()
        assignments = []
        unresolved = []
        for restaurant in restaurants:
            cuisine = restaurant.cuisine.name
            keywords = KEYWORDS.get(cuisine, ())
            if restaurant.name == "McDonald’s":
                keywords = (
                    "big mac",
                    "mcnugget",
                    "cheeseburger",
                    "chicken burger",
                    "fries",
                )
            elif restaurant.name == "KFC":
                keywords = (
                    "chicken nuggets",
                    "spicy chicken wings",
                )
            candidates = [
                item for item in menu_items if item.restaurant_id == restaurant.id
            ]
            candidates.sort(
                key=lambda item: (
                    -sum(word in item.name.lower() for word in keywords),
                    "signature" in item.name.lower(),
                    item.id,
                )
            )
            chosen = None
            for item in candidates:
                source = item.image.url
                if source not in used_sources:
                    chosen = (item, source)
                    break
            if chosen is None:
                unresolved.append((restaurant, "no unique Cloudinary food source"))
            else:
                used_sources.add(chosen[1])
                assignments.append((restaurant, *chosen))

        for restaurant, reason in unresolved:
            self.stderr.write(f"UNRESOLVED {restaurant.id} {restaurant.name}: {reason}")
        if options["dry_run"]:
            for restaurant, item, source in assignments:
                self.stdout.write(
                    f"{restaurant.id}: {restaurant.name} <- {item.name} ({source})"
                )
            self.stdout.write(
                f"DRY RUN: {len(assignments)} ready, {len(unresolved)} unresolved"
            )
            return

        uploaded = 0
        failures = list(unresolved)
        for restaurant, item, source in assignments:
            try:
                data = download(source)
                with transaction.atomic():
                    restaurant.image.save(
                        f"cover-{restaurant.catalog_key}-{restaurant.id}.jpg",
                        ContentFile(data),
                        save=False,
                    )
                    restaurant.save(update_fields=["image"])
                uploaded += 1
            except Exception as exc:
                failures.append((restaurant, str(exc)))
                self.stderr.write(
                    f"FAILED {restaurant.id} {restaurant.name}: {exc}"
                )

        manifest = Path(options["manifest"])
        if not manifest.is_absolute():
            manifest = Path.cwd() / manifest
        if not manifest.parent.exists():
            manifest = Path(__file__).resolve().parents[4] / options["manifest"]
        manifest.parent.mkdir(parents=True, exist_ok=True)
        with manifest.open("a", encoding="utf-8") as file:
            file.write("\n\n## Restaurant-only Cloudinary food-cover refresh\n\n")
            file.write(
                f"Processed {len(restaurants)} restaurants; uploaded {uploaded}; "
                f"unresolved {len(failures)}. Menu-item fields were not modified.\n\n"
            )
            file.write("| ID | Restaurant | Source menu product | Source Cloudinary URL |\n")
            file.write("|---:|---|---|---|\n")
            for restaurant, item, source in assignments:
                file.write(f"| {restaurant.id} | {restaurant.name} | {item.name} | {source} |\n")
            if failures:
                file.write("\nUnresolved:\n")
                for restaurant, reason in failures:
                    file.write(f"- {restaurant.id} {restaurant.name}: {reason}\n")

        if failures:
            raise CommandError(
                f"Completed {uploaded}/{len(restaurants)} restaurant uploads; "
                f"{len(failures)} unresolved. Backup: {backup}"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {uploaded}/{len(restaurants)} restaurant covers. "
                f"Backup: {backup}"
            )
        )
