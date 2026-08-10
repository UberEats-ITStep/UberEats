from rest_framework import serializers

from .models import (
    Category, Cuisine, DEFAULT_MENU_ITEM_IMAGE_URL,
    DEFAULT_RESTAURANT_IMAGE_URL, MenuItem, OpeningHours, Restaurant,
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
    image = serializers.SerializerMethodField()

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
            "is_available",
            "unavailable_reason",
            "is_vegetarian",
            "is_vegan",
            "calories",
        )

    def get_image(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_MENU_ITEM_IMAGE_URL)

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class RestaurantMenuItemSerializer(ImageURLMixin,serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.SerializerMethodField()

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
            "is_available",
            "unavailable_reason",
        )

    def get_image(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_MENU_ITEM_IMAGE_URL)


class RestaurantListSerializer(ImageURLMixin,serializers.ModelSerializer):
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
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_MENU_ITEM_IMAGE_URL)

    def get_is_open_now(self, obj):
        return obj.is_open_now

    def validate(self, data):
        lat = data.get("latitude")
        lng = data.get("longitude")
        if (lat is None) != (lng is None):
            raise serializers.ValidationError(
                "Latitude and longitude must both be set, or both be empty."
            )
        return data


RestaurantSerializer = RestaurantListSerializer


class RestaurantDetailSerializer(ImageURLMixin, serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)
    is_open_now = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    def get_is_open_now(self, obj):
        return obj.is_open_now

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
            "categories",
        )

    def get_image_url(self, obj):
        return self._resolve_image_url(obj.image, obj.image_url, DEFAULT_RESTAURANT_IMAGE_URL)

class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = "__all__"