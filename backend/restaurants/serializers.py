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
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

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
            "slug",
        )

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


class RestaurantMenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

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
            "slug",
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
            "review_count",
            "delivery_time",
            "is_open_now",
        )

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
    def validate(self, data):
        opens_at = data.get("opens_at", getattr(self.instance, "opens_at", None))
        closes_at = data.get("closes_at", getattr(self.instance, "closes_at", None))
        if opens_at == closes_at:
            raise serializers.ValidationError({
                "closes_at": "Closing time must differ from opening time."
            })
        return data

    class Meta:
        model = OpeningHours
        fields = ("id", "day_type", "opens_at", "closes_at")


class RestaurantDetailSerializer(serializers.ModelSerializer):
    cuisine_name = serializers.CharField(source="cuisine.name", read_only=True)
    is_open_now = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    opening_hours = OpeningHoursSerializer(many=True, read_only=True)

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
