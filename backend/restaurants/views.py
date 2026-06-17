from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Restaurant, Category, MenuItem
from .serializators import RestaurantSerializer,CategorySerializer,MenuItemSerializer
# Create your views here.

class RestaurantCRUD(ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class CategoryCRUD(ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = CategorySerializer
    
class MenuItemCRUD(ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = MenuItemSerializer
    