from rest_framework import serializers

from .models import Category, Cuisine, MenuItem, Restaurant, OpeningHours


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
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

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class RestaurantMenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

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


class RestaurantListSerializer(serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)
    is_open_now = serializers.SerializerMethodField()

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
            "delivery_time",
            "is_open_now",
        )

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


class RestaurantDetailSerializer(serializers.ModelSerializer):
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
                RestaurantMenuItemSerializer(item).data
            )

        return list(grouped_categories.values())

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
            "delivery_time",
            "is_open_now",
            "categories",
        )


class OpeningHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpeningHours
        fields = "__all__"