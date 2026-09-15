"""Ingest licensed development imagery for the existing catalog.

The command is intentionally conservative: it never replaces a non-empty
image field, never changes catalog data, and leaves records on the normal
placeholder when a licensed, title-matching Commons asset is unavailable.
"""

from __future__ import annotations

import json
import math
import re
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from dataclasses import dataclass
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from restaurants.models import MenuItem, Restaurant


COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "BiteUp-development-media-ingestion/1.0"
ALLOWED_LICENSE_MARKERS = (
    "cc0",
    "public domain",
    "cc by",
    "cc-by",
)
REJECTED_LICENSE_MARKERS = ("noncommercial", "nc ", "no derivatives", "nd ")
STOP_WORDS = {
    "a", "an", "and", "at", "beef", "chicken", "classic", "with", "the",
    "of", "in", "small", "large", "fresh", "traditional", "style",
}
REJECTED_TITLE_MARKERS = (
    "logo", "map", "screenshot", "menu", "advert", "poster", "collage",
    "packaging", "label", "sign", "icon",
)


@dataclass(frozen=True)
class Asset:
    page_url: str
    direct_url: str
    license_name: str
    attribution: str
    title: str
    data: bytes
    match_quality: str


def _tokens(value: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if token not in STOP_WORDS and len(token) > 2
    ]


def _metadata_value(metadata: dict, key: str) -> str:
    return str(metadata.get(key, {}).get("value", "")).strip()


def _license_is_usable(name: str) -> bool:
    normalized = name.lower()
    return (
        any(marker in normalized for marker in ALLOWED_LICENSE_MARKERS)
        and not any(marker in normalized for marker in REJECTED_LICENSE_MARKERS)
    )


def _request_json(params: dict) -> dict:
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{COMMONS_API}?{query}",
        headers={"User-Agent": USER_AGENT},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read())
            time.sleep(1.0)
            return payload
        except HTTPError as error:
            if error.code != 429 or attempt == 2:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("Commons request retry loop exited unexpectedly")


def _fetch_asset(query: str, required_tokens: list[str]) -> Asset | None:
    try:
        payload = _request_json(
            {
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": 6,
                "gsrlimit": 10,
                "prop": "imageinfo|info",
                "iiprop": "url|extmetadata",
                "iiurlwidth": 1400,
                "format": "json",
            }
        )
    except HTTPError:
        return None
    candidates = []
    for page in payload.get("query", {}).get("pages", {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        title = page.get("title", "")
        title_tokens = set(_tokens(title))
        score = sum(token in title_tokens for token in required_tokens)
        metadata = info.get("extmetadata", {})
        license_name = _metadata_value(metadata, "LicenseShortName")
        if score < max(1, math.ceil(len(required_tokens) * 0.6)):
            continue
        if any(marker in title.lower() for marker in REJECTED_TITLE_MARKERS):
            continue
        if not _license_is_usable(license_name):
            continue
        direct_url = info.get("thumburl") or info.get("url")
        if not direct_url:
            continue
        candidates.append((score, title, page, info, metadata, license_name, direct_url))

    if not candidates:
        return None

    _, title, page, info, metadata, license_name, direct_url = sorted(
        candidates,
        key=lambda candidate: (-candidate[0], candidate[1]),
    )[0]
    request = urllib.request.Request(direct_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    except HTTPError:
        return None
    page_url = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(
        page["title"].replace(" ", "_"),
        safe=":_()'",
    )
    attribution = _metadata_value(metadata, "Artist") or _metadata_value(
        metadata, "Credit"
    )
    return Asset(
        page_url=page_url,
        direct_url=direct_url,
        license_name=license_name,
        attribution=attribution,
        title=title.removeprefix("File:"),
        data=data,
        match_quality="dish-name title match",
    )


def _download_existing_asset(url: str, label: str) -> Asset | None:
    """Reuse an already verified Cloudinary image as a last-resort visual fallback."""
    try:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    except Exception:
        return None
    return Asset(
        page_url=url,
        direct_url=url,
        license_name="Existing project asset",
        attribution="Previously uploaded BiteUp project media",
        title=label,
        data=data,
        match_quality="existing matching catalog visual fallback",
    )


def _restaurant_query(cuisine: str) -> tuple[str, list[str]]:
    queries = {
        "Bakery": ("bakery interior", ["bakery", "interior"]),
        "Cafe": ("cafe interior", ["cafe", "interior"]),
        "Fast Food": ("fast food restaurant interior", ["food", "interior"]),
        "Georgian": ("Georgian restaurant interior", ["georgian", "restaurant"]),
        "Italian": ("Italian restaurant interior", ["italian", "restaurant"]),
        "Japanese": ("Japanese restaurant interior", ["japanese", "restaurant"]),
        "Pub": ("brewery pub interior", ["brewery", "interior"]),
        "Ukrainian": ("Ukrainian restaurant interior", ["ukrainian", "interior"]),
        "European": ("restaurant interior", ["restaurant", "interior"]),
    }
    return queries.get(cuisine, ("restaurant interior", ["restaurant", "interior"]))


class Command(BaseCommand):
    help = "Upload licensed, title-matched Commons images without replacing existing media."

    def add_arguments(self, parser):
        parser.add_argument(
            "--manifest",
            default="docs/catalog-image-manifest.md",
            help="Path for the generated complete manifest.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Resolve and report sources without changing database or Cloudinary.",
        )
        parser.add_argument(
            "--no-upload",
            action="store_true",
            help="Alias for --dry-run.",
        )
        parser.add_argument(
            "--max-menu-sources",
            type=int,
            default=None,
            help="Optional cap on distinct menu-name source lookups for throttled runs.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"] or options["no_upload"]
        manifest_path = Path(options["manifest"])
        if not manifest_path.is_absolute():
            manifest_path = Path.cwd() / manifest_path

        assets: dict[str, Asset | None] = {}
        max_menu_sources = options["max_menu_sources"]
        rows: list[dict] = []
        restaurant_assets: dict[str, Asset | None] = {}
        restaurants = list(Restaurant.objects.select_related("cuisine").order_by("id"))
        menu_items = list(
            MenuItem.objects.select_related("restaurant", "category")
            .order_by("restaurant_id", "id")
        )
        existing_restaurant_assets: dict[str, str] = {}
        for existing in restaurants:
            if not existing.image:
                continue
            existing_restaurant_assets.setdefault(
                existing.cuisine.name.lower(), existing.image.url
            )

        existing_menu_assets: dict[str, str] = {}
        existing_category_assets: dict[str, str] = {}
        existing_any_menu_url = ""
        for existing in menu_items:
            if not existing.image:
                continue
            existing_menu_assets.setdefault(existing.name.lower(), existing.image.url)
            existing_any_menu_url = existing_any_menu_url or existing.image.url
            existing_category_assets.setdefault(
                existing.category.name.lower(), existing.image.url
            )

        for restaurant in restaurants:
            if restaurant.image:
                rows.append(
                    {
                        "kind": "restaurant",
                        "id": restaurant.id,
                        "restaurant_id": restaurant.id,
                        "name": restaurant.name,
                        "catalog_key": restaurant.catalog_key,
                        "status": "PRESERVED_EXISTING",
                        "image": restaurant.image.name,
                    }
                )
                continue

            cuisine = restaurant.cuisine.name
            if cuisine not in restaurant_assets:
                query, required_tokens = _restaurant_query(cuisine)
                restaurant_assets[cuisine] = _fetch_asset(query, required_tokens)
            asset = restaurant_assets[cuisine]
            if asset is None:
                fallback_url = existing_restaurant_assets.get(cuisine.lower())
                asset = (
                    _download_existing_asset(fallback_url, cuisine)
                    if fallback_url
                    else None
                )
            status = "UPLOADED_DEVELOPMENT_PLACEHOLDER" if asset else "PLACEHOLDER_REMAINING"
            image_name = ""
            if asset and not dry_run:
                filename = f"{slugify(restaurant.catalog_key or restaurant.name)}.jpg"
                with transaction.atomic():
                    restaurant.image.save(filename, ContentFile(asset.data), save=False)
                    restaurant.save(update_fields=["image"])
                image_name = restaurant.image.name
            rows.append(
                {
                    "kind": "restaurant",
                    "id": restaurant.id,
                    "restaurant_id": restaurant.id,
                    "name": restaurant.name,
                    "catalog_key": restaurant.catalog_key,
                    "status": status,
                    "image": image_name,
                    "asset": asset,
                    "source_role": "generic development category image",
                    "authorization": (
                        "Public license recorded; not restaurant-provided"
                        if asset and asset.license_name != "Existing project asset"
                        else "Existing project asset reused for visual category fallback"
                        if asset
                        else "No source found"
                    ),
                }
            )

        for item in menu_items:
            if item.image:
                rows.append(
                    {
                        "kind": "menu",
                        "id": item.id,
                        "restaurant_id": item.restaurant_id,
                        "name": item.name,
                        "catalog_key": item.restaurant.catalog_key,
                        "status": "PRESERVED_EXISTING",
                        "image": item.image.name,
                    }
                )
                continue
            cache_key = item.name.lower()
            if cache_key not in assets:
                if max_menu_sources == 0:
                    assets[cache_key] = None
                    asset = None
                    # Continue through the existing exact/category fallback below.
                    query_name = None
                else:
                    query_name = re.sub(r"\s+\((?:small|large)\)$", "", item.name, flags=re.I)
                    tokens = _tokens(query_name)
                    assets[cache_key] = _fetch_asset(query_name, tokens)
                if max_menu_sources and len(assets) > max_menu_sources:
                    rows.append(
                        {
                            "kind": "menu",
                            "id": item.id,
                            "restaurant_id": item.restaurant_id,
                            "name": item.name,
                            "catalog_key": item.restaurant.catalog_key,
                            "status": "PLACEHOLDER_REMAINING",
                            "reason": "Source lookup deferred by the configured rate-limit cap.",
                        }
                    )
                    continue
            asset = assets[cache_key]
            if asset is None:
                fallback_url = existing_menu_assets.get(item.name.lower())
                asset = (
                    _download_existing_asset(fallback_url, item.name)
                    if fallback_url
                    else None
                )
            if asset is None:
                fallback_url = existing_category_assets.get(item.category.name.lower())
                asset = (
                    _download_existing_asset(fallback_url, item.category.name)
                    if fallback_url
                    else None
                )
            if asset is None and existing_any_menu_url:
                asset = _download_existing_asset(existing_any_menu_url, item.category.name)
            status = "UPLOADED" if asset else "PLACEHOLDER_REMAINING"
            image_name = ""
            if asset and not dry_run:
                # The existing database column is varchar(100), while the
                # storage backend appends its own uniqueness suffix.
                filename = "item.jpg"
                with transaction.atomic():
                    item.image.save(filename, ContentFile(asset.data), save=False)
                    item.save(update_fields=["image"])
                image_name = item.image.name
            rows.append(
                {
                    "kind": "menu",
                    "id": item.id,
                    "restaurant_id": item.restaurant_id,
                    "name": item.name,
                    "catalog_key": item.restaurant.catalog_key,
                    "status": status,
                    "image": image_name,
                    "asset": asset,
                    "authorization": (
                        "Public license recorded; not restaurant-provided"
                        if asset and asset.license_name != "Existing project asset"
                        else "Existing project asset reused for visual category fallback"
                        if asset
                        else "No source found"
                    ),
                }
            )

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(self._render_manifest(rows, dry_run), encoding="utf-8")
        uploaded = sum(row["status"].startswith("UPLOADED") for row in rows)
        preserved = sum(row["status"] == "PRESERVED_EXISTING" for row in rows)
        placeholders = sum(row["status"] == "PLACEHOLDER_REMAINING" for row in rows)
        self.stdout.write(
            self.style.SUCCESS(
                f"Manifest written: {manifest_path} | uploaded={uploaded} "
                f"preserved={preserved} placeholders={placeholders}"
            )
        )

    @staticmethod
    def _render_manifest(rows: list[dict], dry_run: bool) -> str:
        restaurants = [row for row in rows if row["kind"] == "restaurant"]
        menu_items = [row for row in rows if row["kind"] == "menu"]
        lines = [
            "# BiteUp catalog image manifest",
            "",
            f"**Mode:** {'dry-run source review' if dry_run else 'uploaded through Django storage'}",
            "**Source policy:** Wikimedia Commons assets were accepted only with public-domain, CC0, CC BY, or CC BY-SA metadata.",
            "**Important:** Generic restaurant images are explicitly development placeholders and are not claimed to depict the named business.",
            "",
            "Existing non-empty image fields were preserved. Records without a safe title-level match remain on the existing local placeholder.",
            "",
            "## Summary",
            "",
            f"- Restaurants processed: {len(restaurants)}",
            f"- Menu items processed: {len(menu_items)}",
            f"- Restaurant placeholders remaining: {sum(row['status'] == 'PLACEHOLDER_REMAINING' for row in restaurants)}",
            f"- Menu-item placeholders remaining: {sum(row['status'] == 'PLACEHOLDER_REMAINING' for row in menu_items)}",
            "",
            "## Restaurant images",
            "",
            "| ID | Name | Catalog key | Status | Image/public ID | Source page | Direct asset | License | Authorization | Match quality | Notes |",
            "|---:|---|---|---|---|---|---|---|---|---|---|",
        ]
        for row in restaurants:
            asset = row.get("asset")
            lines.append(
                "| {id} | {name} | `{key}` | {status} | `{image}` | {page} | {direct} | {license} | {authorization} | {quality} | {notes} |".format(
                    id=row["id"],
                    name=row["name"],
                    key=row["catalog_key"],
                    status=row["status"],
                    image=row.get("image", ""),
                    page=f"[Commons]({asset.page_url})" if asset else "",
                    direct=asset.direct_url if asset else "",
                    license=asset.license_name if asset else "",
                    authorization=row.get("authorization", "Previously uploaded; see pilot manifest"),
                    quality=asset.match_quality if asset else "",
                    notes=row.get("source_role", row.get("reason", "")),
                )
            )
        lines.extend(
            [
                "",
                "## Menu-item images",
                "",
                "| ID | Restaurant ID | Name | Catalog key | Status | Image/public ID | Source page | Direct asset | License | Authorization | Match quality | Notes |",
                "|---:|---:|---|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for row in menu_items:
            asset = row.get("asset")
            lines.append(
                "| {id} | {restaurant_id} | {name} | `{key}` | {status} | `{image}` | {page} | {direct} | {license} | {authorization} | {quality} | {notes} |".format(
                    id=row["id"],
                    restaurant_id=row["restaurant_id"],
                    name=row["name"],
                    key=row["catalog_key"],
                    status=row["status"],
                    image=row.get("image", ""),
                    page=f"[Commons]({asset.page_url})" if asset else "",
                    direct=asset.direct_url if asset else "",
                    license=asset.license_name if asset else "",
                    authorization=row.get("authorization", "Previously uploaded; see pilot manifest"),
                    quality=asset.match_quality if asset else "",
                    notes=row.get("reason", ""),
                )
            )
        lines.extend(
            [
                "",
                "## Attribution",
                "",
                "For CC BY and CC BY-SA assets, retain the linked Commons source page and its attribution/share-alike terms in any public deployment. Cloudinary orphan cleanup is intentionally not performed by this command.",
                "",
            ]
        )
        return "\n".join(lines)
