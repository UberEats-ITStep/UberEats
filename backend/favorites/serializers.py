from .models import Favorite
from restaurants .serializers import RestaurantListSerializer
from rest_framework import serializers

class FavoriteSerializer(serializers.ModelSerializer):
    restaurant_detail = RestaurantListSerializer(source="restaurant", read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "restaurant", "restaurant_detail", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        favorite, _ = Favorite.objects.get_or_create(
            user=validated_data["user"], restaurant=validated_data["restaurant"]
        )
        return favorite