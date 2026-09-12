from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse


RIVNE_LATITUDE_RANGE = (Decimal("50.55"), Decimal("50.70"))
RIVNE_LONGITUDE_RANGE = (Decimal("26.15"), Decimal("26.36"))


class CatalogValidationError(ValueError):
    """Raised when a catalog record is incomplete or outside Rivne."""


def _as_decimal(value, field_name, catalog_key):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise CatalogValidationError(
            f"{catalog_key}: {field_name} must be a decimal value."
        ) from error


def _require_fields(record, field_names):
    catalog_key = record.get("catalog_key", "<missing catalog_key>")
    missing = [field for field in field_names if not record.get(field)]
    if missing:
        raise CatalogValidationError(
            f"{catalog_key}: missing required fields: {', '.join(missing)}."
        )


def validate_catalog(records):
    """Validate catalog records before any database write is attempted."""
    catalog_keys = set()

    for record in records:
        _require_fields(
            record,
            (
                "catalog_key",
                "name",
                "description",
                "address",
                "latitude",
                "longitude",
                "cuisine",
                "provenance",
            ),
        )
        catalog_key = record["catalog_key"]
        if catalog_key in catalog_keys:
            raise CatalogValidationError(f"Duplicate catalog_key: {catalog_key}.")
        catalog_keys.add(catalog_key)

        for field_name in ("catalog_key", "name", "address"):
            if "demo" in str(record[field_name]).casefold():
                raise CatalogValidationError(
                    f"{catalog_key}: demo values are not allowed in {field_name}."
                )

        latitude = _as_decimal(record["latitude"], "latitude", catalog_key)
        longitude = _as_decimal(record["longitude"], "longitude", catalog_key)
        if not RIVNE_LATITUDE_RANGE[0] <= latitude <= RIVNE_LATITUDE_RANGE[1]:
            raise CatalogValidationError(f"{catalog_key}: latitude is outside Rivne.")
        if not RIVNE_LONGITUDE_RANGE[0] <= longitude <= RIVNE_LONGITUDE_RANGE[1]:
            raise CatalogValidationError(f"{catalog_key}: longitude is outside Rivne.")

        provenance = record["provenance"]
        source_url = provenance.get("source_url", "")
        if urlparse(source_url).scheme != "https":
            raise CatalogValidationError(f"{catalog_key}: provenance URL must use HTTPS.")
        if provenance.get("license") != "ODbL-1.0":
            raise CatalogValidationError(
                f"{catalog_key}: provenance license must be ODbL-1.0."
            )
        try:
            date.fromisoformat(provenance.get("verified_at", ""))
        except ValueError as error:
            raise CatalogValidationError(
                f"{catalog_key}: provenance verified_at must be an ISO date."
            ) from error

        image_url = record.get("image_url", "")
        if "picsum.photos" in image_url.casefold():
            raise CatalogValidationError(
                f"{catalog_key}: picsum.photos cannot be used in the production catalog."
            )

        hours = record.get("opening_hours", {})
        if hours and set(hours) != {"weekday", "weekend"}:
            raise CatalogValidationError(
                f"{catalog_key}: opening_hours must include weekday and weekend."
            )
        for day_type, interval in hours.items():
            if not isinstance(interval, tuple) or len(interval) != 2 or interval[0] == interval[1]:
                raise CatalogValidationError(
                    f"{catalog_key}: {day_type} opening hours are invalid."
                )

        for item in record.get("menu_items", ()):
            _require_fields(item, ("name", "category", "price"))
            if "demo" in item["name"].casefold():
                raise CatalogValidationError(
                    f"{catalog_key}: demo menu items are not allowed."
                )
            if _as_decimal(item["price"], "menu item price", catalog_key) <= 0:
                raise CatalogValidationError(
                    f"{catalog_key}: menu item price must be greater than zero."
                )
            if item.get("is_vegan") and not item.get("is_vegetarian"):
                raise CatalogValidationError(
                    f"{catalog_key}: vegan menu items must be vegetarian."
                )