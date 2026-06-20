from decimal import Decimal

from django.test import TestCase

from .models import Category, MenuItem, Restaurant


class RestaurantModelTests(TestCase):
    def test_restaurant_category_and_menuitem_relationships_work(self):
        restaurant = Restaurant.objects.create(name='Sushi Place')
        category = Category.objects.create(restaurant=restaurant, name='Rolls')
        menu_item = MenuItem.objects.create(
            restaurant=restaurant,
            category=category,
            name='Salmon Roll',
            price=Decimal('12.50'),
        )

        self.assertEqual(restaurant.categories.count(), 1)
        self.assertEqual(restaurant.menu_items.count(), 1)
        self.assertEqual(category.menu_items.count(), 1)
        self.assertEqual(menu_item.restaurant, restaurant)
        self.assertEqual(menu_item.category, category)
        self.assertEqual(menu_item.price, Decimal('12.50'))
