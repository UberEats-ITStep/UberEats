from rest_framework import serializers
from .models import Restaurant, Category, MenuItem


class RestaurantSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    deliveryTime = serializers.CharField(source='delivery_time')

    class Meta:
        model = Restaurant
        fields = (
            'id',
            'name',
            'description',
            'rating',
            'deliveryTime',
            'categories',
            'image',
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"