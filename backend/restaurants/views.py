from django.db.models import Prefetch
from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Cuisine, MenuItem, Restaurant
from .serializers import (
    CategorySerializer,
    CuisineSerializer,
    MenuItemSerializer,
    RestaurantDetailSerializer,
    RestaurantListSerializer,
)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RestaurantListSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Restaurant.objects.order_by("id").select_related("cuisine").prefetch_related("opening_hours")

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
    pagination_class = StandardPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "category": ["exact"],
        "restaurant": ["exact"],
        "is_available": ["exact"],
        "price": ["gte", "lte"],
    }
    search_fields = ["name"]
    ordering_fields = ["price", "name"]
    ordering = ["category", "name"]


class CuisineCRUD(viewsets.ModelViewSet):
    queryset = Cuisine.objects.order_by("id")
    serializer_class = CuisineSerializer
