import random
from decimal import Decimal
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, Category, MenuItem

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with realistic demo data for local development'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting database seeding...'))
        
        self._create_users()
        self._create_restaurants_and_menus()
        
        self.stdout.write(self.style.SUCCESS('\nDatabase successfully seeded!'))

    def _create_users(self):
        self.stdout.write(self.style.HTTP_INFO('\nCreating users...'))
        
        # Admin User
        admin_email = 'admin@example.com'
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                username='admin',
                password='password123',
                role='Admin'
            )
            self.stdout.write(self.style.SUCCESS(f' Created Admin: {admin_email}'))
        else:
            self.stdout.write(f' Admin {admin_email} already exists.')

        # Client User
        client_email = 'client@example.com'
        client_user, created = User.objects.get_or_create(
            email=client_email,
            defaults={'username': 'client_user', 'role': 'Client'}
        )
        if created:
            client_user.set_password('password123')
            client_user.save()
            self.stdout.write(self.style.SUCCESS(f' Created Client: {client_email}'))
        else:
            self.stdout.write(f' Client {client_email} already exists.')

        # Courier User
        courier_email = 'courier@example.com'
        courier_user, created = User.objects.get_or_create(
            email=courier_email,
            defaults={'username': 'courier_user', 'role': 'Courier'}
        )
        if created:
            courier_user.set_password('password123')
            courier_user.save()
            self.stdout.write(self.style.SUCCESS(f' Created Courier: {courier_email}'))
        else:
            self.stdout.write(f' Courier {courier_email} already exists.')

    def _create_restaurants_and_menus(self):
        self.stdout.write(self.style.HTTP_INFO('\nCreating restaurants, categories, and menu items...'))

        restaurants_data = [
            {
                "name": "Pizza Paradise",
                "description": "Wood-fired pizzas, comforting sides, and classic Italian desserts.",
                "rating": 4.7,
                "delivery_time": "25-40 min",
                "image": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?auto=format&fit=crop&w=800&q=80",
                "categories": ["Pizza", "Sides", "Drinks", "Desserts"],
                "items": {
                    "Pizza": [("Margherita", 12.99), ("Pepperoni", 14.99), ("BBQ Chicken", 16.99), ("Hawaiian", 15.50)],
                    "Sides": [("Garlic Bread", 4.99), ("Mozzarella Sticks", 6.99), ("Chicken Wings", 8.99)],
                    "Drinks": [("Coca Cola", 2.50), ("Sprite", 2.50), ("Water", 1.50)],
                    "Desserts": [("Tiramisu", 5.99), ("Cheesecake", 6.50)]
                }
            },
            {
                "name": "Burger Joint",
                "description": "Juicy burgers, crispy sides, and hand-spun shakes made to order.",
                "rating": 4.6,
                "delivery_time": "20-35 min",
                "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=800&q=80",
                "categories": ["Burgers", "Sides", "Drinks", "Shakes"],
                "items": {
                    "Burgers": [("Classic Cheeseburger", 9.99), ("Bacon Double", 13.99), ("Veggie Burger", 10.99)],
                    "Sides": [("French Fries", 3.99), ("Onion Rings", 4.99), ("Sweet Potato Fries", 4.50)],
                    "Drinks": [("Iced Tea", 2.00), ("Lemonade", 2.50)],
                    "Shakes": [("Vanilla Shake", 5.00), ("Chocolate Shake", 5.00), ("Strawberry Shake", 5.00)]
                }
            },
            {
                "name": "Sushi World",
                "description": "Fresh sushi rolls, nigiri, and Japanese favourites prepared daily.",
                "rating": 4.8,
                "delivery_time": "30-45 min",
                "image": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=800&q=80",
                "categories": ["Sushi Rolls", "Nigiri", "Appetizers", "Drinks"],
                "items": {
                    "Sushi Rolls": [("California Roll", 6.99), ("Spicy Tuna Roll", 8.99), ("Dragon Roll", 12.99), ("Rainbow Roll", 14.99)],
                    "Nigiri": [("Salmon Nigiri", 5.99), ("Tuna Nigiri", 6.50), ("Eel Nigiri", 7.00)],
                    "Appetizers": [("Edamame", 4.50), ("Miso Soup", 3.50), ("Gyoza", 5.99)],
                    "Drinks": [("Green Tea", 2.00), ("Asahi Beer", 4.50), ("Sake", 8.00)]
                }
            },
            {
                "name": "Taco Town",
                "description": "Street-style tacos, filling burritos, and fresh Mexican sides.",
                "rating": 4.5,
                "delivery_time": "20-35 min",
                "image": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?auto=format&fit=crop&w=800&q=80",
                "categories": ["Tacos", "Burritos", "Sides", "Drinks"],
                "items": {
                    "Tacos": [("Al Pastor Taco", 3.50), ("Carne Asada Taco", 4.00), ("Chicken Taco", 3.50), ("Fish Taco", 4.50)],
                    "Burritos": [("Beef Burrito", 10.99), ("Chicken Burrito", 9.99), ("Bean & Cheese Burrito", 7.99)],
                    "Sides": [("Chips and Guacamole", 5.99), ("Queso Dip", 4.99)],
                    "Drinks": [("Horchata", 3.00), ("Jarritos", 2.50), ("Margarita", 8.00)]
                }
            },
            {
                "name": "The Green Salad",
                "description": "Fresh salads, nourishing bowls, and fruit-packed smoothies.",
                "rating": 4.6,
                "delivery_time": "15-25 min",
                "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80",
                "categories": ["Salads", "Bowls", "Smoothies", "Snacks"],
                "items": {
                    "Salads": [("Caesar Salad", 9.50), ("Greek Salad", 10.00), ("Cobb Salad", 11.50)],
                    "Bowls": [("Quinoa Bowl", 12.00), ("Acai Bowl", 8.50), ("Teriyaki Chicken Bowl", 13.00)],
                    "Smoothies": [("Green Detox", 6.00), ("Berry Blast", 6.00), ("Mango Tango", 6.50)],
                    "Snacks": [("Protein Bites", 4.00), ("Fruit Cup", 3.50)]
                }
            },
            {
                "name": "Pasta House",
                "description": "Italian pasta, pizza, and seasonal salads made with simple ingredients.",
                "rating": 4.7,
                "delivery_time": "30-45 min",
                "image": "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80",
                "categories": ["Pasta", "Pizza", "Salads", "Drinks"],
                "items": {
                    "Pasta": [("Spaghetti Carbonara", 14.50), ("Fettuccine Alfredo", 13.50), ("Penne Arrabbiata", 12.00), ("Lasagna", 15.00)],
                    "Pizza": [("Margherita", 11.99), ("Four Cheese", 13.99)],
                    "Salads": [("House Salad", 6.50), ("Caprese", 8.50)],
                    "Drinks": [("Red Wine", 7.00), ("Sparkling Water", 3.00)]
                }
            },
            {
                "name": "Morning Brew",
                "description": "Specialty coffee, warm pastries, and easy breakfast favourites.",
                "rating": 4.4,
                "delivery_time": "15-25 min",
                "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80",
                "categories": ["Coffee", "Tea", "Pastries", "Breakfast"],
                "items": {
                    "Coffee": [("Espresso", 2.50), ("Latte", 4.00), ("Cappuccino", 4.00), ("Cold Brew", 4.50)],
                    "Tea": [("English Breakfast", 3.00), ("Matcha Latte", 4.50), ("Chai Latte", 4.50)],
                    "Pastries": [("Croissant", 3.50), ("Blueberry Muffin", 3.00), ("Chocolate Chip Cookie", 2.50)],
                    "Breakfast": [("Avocado Toast", 7.50), ("Breakfast Sandwich", 6.50), ("Oatmeal", 5.00)]
                }
            },
            {
                "name": "Steakhouse Grill",
                "description": "Grilled steaks, hearty sides, and classic desserts for dinner at home.",
                "rating": 4.9,
                "delivery_time": "35-50 min",
                "image": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=800&q=80",
                "categories": ["Steaks", "Sides", "Desserts", "Drinks"],
                "items": {
                    "Steaks": [("Ribeye 12oz", 28.00), ("Filet Mignon 8oz", 32.00), ("New York Strip", 26.00)],
                    "Sides": [("Mashed Potatoes", 6.00), ("Creamed Spinach", 7.00), ("Truffle Fries", 8.00)],
                    "Desserts": [("Lava Cake", 9.00), ("New York Cheesecake", 8.50)],
                    "Drinks": [("Old Fashioned", 12.00), ("Craft Beer", 6.00)]
                }
            },
            {
                "name": "Wok & Roll",
                "description": "Asian noodle bowls, rice dishes, and shareable starters.",
                "rating": 4.5,
                "delivery_time": "25-40 min",
                "image": "https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=800&q=80",
                "categories": ["Noodles", "Rice Dishes", "Appetizers", "Drinks"],
                "items": {
                    "Noodles": [("Pad Thai", 12.50), ("Lo Mein", 11.00), ("Pho", 13.00), ("Ramen", 14.00)],
                    "Rice Dishes": [("Chicken Fried Rice", 10.50), ("Pork Fried Rice", 10.50), ("Shrimp Fried Rice", 12.50)],
                    "Appetizers": [("Spring Rolls", 5.00), ("Crab Rangoon", 6.50), ("Dumplings", 6.00)],
                    "Drinks": [("Thai Iced Tea", 4.00), ("Boba Tea", 4.50)]
                }
            },
            {
                "name": "Vegan Haven",
                "description": "Plant-based comfort food, fresh wraps, and dairy-free desserts.",
                "rating": 4.6,
                "delivery_time": "20-35 min",
                "image": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=800&q=80",
                "categories": ["Mains", "Wraps", "Sides", "Desserts"],
                "items": {
                    "Mains": [("Beyond Burger", 13.50), ("Jackfruit BBQ Sandwhich", 12.00), ("Vegan Mac & Cheese", 11.50)],
                    "Wraps": [("Hummus Wrap", 9.50), ("Falafel Wrap", 10.00)],
                    "Sides": [("Roasted Veggies", 5.50), ("Sweet Potato Wedges", 4.50)],
                    "Desserts": [("Vegan Brownie", 4.00), ("Chia Pudding", 5.00)]
                }
            }
        ]

        created_restaurants = 0
        created_categories = 0
        created_items = 0

        for r_data in restaurants_data:
            restaurant, created = Restaurant.objects.update_or_create(
                name=r_data["name"],
                defaults={
                    "description": r_data["description"],
                    "rating": r_data["rating"],
                    "delivery_time": r_data["delivery_time"],
                    "image": r_data["image"],
                }
            )
            if created:
                created_restaurants += 1
            
            for cat_name in r_data["categories"]:
                category, cat_created = Category.objects.get_or_create(
                    restaurant=restaurant,
                    name=cat_name
                )
                if cat_created:
                    created_categories += 1
                
                # Fetch items for this category
                items = r_data["items"].get(cat_name, [])
                for item_name, item_price in items:
                    _, item_created = MenuItem.objects.get_or_create(
                        restaurant=restaurant,
                        category=category,
                        name=item_name,
                        defaults={"price": Decimal(str(item_price))}
                    )
                    if item_created:
                        created_items += 1

        self.stdout.write(self.style.SUCCESS(
            f' Successfully ensured {len(restaurants_data)} restaurants are seeded.'
        ))
        if created_restaurants or created_categories or created_items:
            self.stdout.write(f'  + Created {created_restaurants} new restaurants')
            self.stdout.write(f'  + Created {created_categories} new categories')
            self.stdout.write(f'  + Created {created_items} new menu items')
        else:
            self.stdout.write('  (All restaurants, categories, and items already existed. No duplicates created.)')
