from rest_framework import serializers

from .models import (
    Category, Cuisine, DEFAULT_MENU_ITEM_IMAGE_URL,
    DEFAULT_RESTAURANT_IMAGE_URL, MenuItem, MenuTag, OpeningHours, Restaurant,
)


class ImageURLMixin:
    def _resolve_image_url(self, file_field, legacy_url, default_url):
        request = self.context.get("request")
        if file_field:
            try:
                url = file_field.url
            except ValueError:
                url = None
            if url:
                return request.build_absolute_uri(url) if request else url
        if legacy_url:
            return legacy_url
        if default_url and request:
            return request.build_absolute_uri(default_url)
        return default_url


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(ImageURLMixin, serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=MenuTag.objects.all(), required=False)

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "restaurant",
            "category",
            "name",
            "description",
            "price",
            "image",
            "image_url",
            "is_available",
            "unavailable_reason",
            "is_vegetarian",
            "is_vegan",
            "calories",
            "tags",
            "slug",
        )
        read_only_fields = ("slug",)

    def get_image_url(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_MENU_ITEM_IMAGE_URL)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Keep the established `image` response while also exposing the legacy
        # `image_url` alias. Unlike SerializerMethodField, ImageField stays
        # writable for multipart uploads and explicit removal with null.
        data["image"] = data["image_url"]
        return data

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate(self, data):
        is_available = data.get(
            "is_available", getattr(self.instance, "is_available", True)
        )
        reason = data.get(
            "unavailable_reason",
            getattr(self.instance, "unavailable_reason", ""),
        )
        if is_available and reason:
            raise serializers.ValidationError({
                "unavailable_reason": "Available items cannot have an unavailable reason."
            })
        if not is_available and not reason.strip():
            raise serializers.ValidationError({
                "unavailable_reason": "Unavailable items must include a reason."
            })
        return data


class RestaurantMenuItemSerializer(ImageURLMixin, serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=MenuTag.objects.all(), required=False)

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "category",
            "category_name",
            "name",
            "description",
            "price",
            "image",
            "image_url",
            "is_available",
            "unavailable_reason",
            "is_vegetarian",
            "is_vegan",
            "calories",
            "tags",
            "slug",
        )

    def get_image_url(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_MENU_ITEM_IMAGE_URL)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["image"] = data["image_url"]
        return data


class RestaurantListSerializer(ImageURLMixin, serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)
    is_open_now = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = (
            "id",
            "name",
            "description",
            "image_url",
            "address",
            "latitude",
            "longitude",
            "cuisine",
            "cuisine_name",
            "rating",
            "review_count",
            "delivery_time",
            "is_open_now",
        )

    def get_image_url(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_RESTAURANT_IMAGE_URL)

    def get_is_open_now(self, obj):
        return obj.is_open_now

    def validate(self, data):
        lat = data.get("latitude", getattr(self.instance, "latitude", None))
        lng = data.get("longitude", getattr(self.instance, "longitude", None))
        if (lat is None) != (lng is None):
            missing_field = "longitude" if lng is None else "latitude"
            raise serializers.ValidationError({
                missing_field: "Latitude and longitude must both be set, or both be empty."
            })
        return data


RestaurantSerializer = RestaurantListSerializer


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = ("id", "day_type", "opens_at", "closes_at")

    def validate(self, data):
        opens_at = data.get("opens_at", getattr(self.instance, "opens_at", None))
        closes_at = data.get("closes_at", getattr(self.instance, "closes_at", None))
        if opens_at == closes_at:
            raise serializers.ValidationError({
                "closes_at": "Closing time must differ from opening time."
            })
        return data


class RestaurantDetailSerializer(ImageURLMixin, serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)
    is_open_now = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = (
            "id",
            "name",
            "description",
            "image_url",
            "address",
            "latitude",
            "longitude",
            "cuisine",
            "cuisine_name",
            "rating",
            "review_count",
            "delivery_time",
            "is_open_now",
            "opening_hours",
            "categories",
        )

    def get_is_open_now(self, obj):
        return obj.is_open_now

    def get_image_url(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_RESTAURANT_IMAGE_URL)

    def get_categories(self, obj):
        grouped_categories = {}

        for item in obj.menu_items.all():
            category_id = item.category_id
            if category_id not in grouped_categories:
                grouped_categories[category_id] = {
                    "id": category_id,
                    "name": item.category.name,
                    "menu_items": [],
                }

            grouped_categories[category_id]["menu_items"].append(
                RestaurantMenuItemSerializer(item, context=self.context).data
            )

        return list(grouped_categories.values())
