from django.contrib import admin

from .models import Category, Cuisine, MenuItem, Restaurant


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name")


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = ("name", "address")
    list_display = ("id", "name", "cuisine", "rating", "delivery_time")
    list_select_related = ("cuisine",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("id", "name", "restaurant", "category", "price", "is_available")
    list_select_related = ("restaurant", "category")
