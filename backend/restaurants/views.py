from django.db.models import Prefetch
from rest_framework import viewsets

from .models import Category, Cuisine, MenuItem, Restaurant
from .serializers import (
    CategorySerializer,
    CuisineSerializer,
    MenuItemSerializer,
    RestaurantDetailSerializer,
    RestaurantListSerializer,
)


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RestaurantListSerializer

    def get_queryset(self):
        queryset = Restaurant.objects.order_by("id").select_related("cuisine")

        if self.action == "retrieve":
            return queryset.prefetch_related(
                Prefetch(
                    "menu_items",
                    queryset=MenuItem.objects.order_by("id").select_related("category"),
                )
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RestaurantDetailSerializer
        return RestaurantListSerializer


class CategoryCRUD(viewsets.ModelViewSet):
    queryset = Category.objects.order_by("id")
    serializer_class = CategorySerializer


class MenuItemCRUD(viewsets.ModelViewSet):
    queryset = MenuItem.objects.order_by("id").select_related("restaurant", "category")
    serializer_class = MenuItemSerializer


class CuisineCRUD(viewsets.ModelViewSet):
    queryset = Cuisine.objects.order_by("id")
    serializer_class = CuisineSerializer
