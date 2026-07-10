from rest_framework import serializers

from .models import Category, Cuisine, MenuItem, Restaurant


class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
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
            "image_url",
            "is_available",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


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
            "image_url",
            "is_available",
        )


class RestaurantListSerializer(serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)

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
        )


RestaurantSerializer = RestaurantListSerializer


class RestaurantDetailSerializer(serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)
    categories = serializers.SerializerMethodField()

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
            "categories",
        )
