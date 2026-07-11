from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase

from .models import Category, MenuItem, Restaurant


class RestaurantModelTests(TestCase):
    def test_restaurant_category_and_menuitem_relationships_work(self):
        restaurant = Restaurant.objects.create(
            name='Sushi Place',
            description='Fresh sushi and Japanese favourites.',
            rating=4.8,
            delivery_time='30-45 min',
            image='https://example.com/sushi-place.jpg',
        )
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


class RestaurantListApiTests(APITestCase):
    def test_list_returns_the_restaurant_card_contract(self):
        restaurant = Restaurant.objects.create(
            name='Sushi Place',
            description='Fresh rolls and nigiri.',
            rating=4.8,
            delivery_time='30-45 min',
            image='https://example.com/sushi.jpg',
        )
        Category.objects.create(restaurant=restaurant, name='Sushi')
        Category.objects.create(restaurant=restaurant, name='Japanese')

        response = self.client.get('/api/restaurants/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{
            'id': restaurant.id,
            'name': 'Sushi Place',
            'description': 'Fresh rolls and nigiri.',
            'rating': 4.8,
            'deliveryTime': '30-45 min',
            'categories': ['Sushi', 'Japanese'],
            'image': 'https://example.com/sushi.jpg',
        }])
