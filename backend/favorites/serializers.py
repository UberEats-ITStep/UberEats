from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from restaurants.serializers import RestaurantListSerializer

from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    restaurant_detail = RestaurantListSerializer(source="restaurant", read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "user", "restaurant", "restaurant_detail", "created_at")
        read_only_fields = ("id", "created_at")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "restaurant"),
                message="This restaurant is already in your favorites.",
            )
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return Favorite.objects.create(**validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {"restaurant": "This restaurant is already in your favorites."}
            ) from error
