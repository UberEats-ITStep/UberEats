from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from restaurants.models import Category, Cuisine, MenuItem, OpeningHours, Restaurant


User = get_user_model()


def _image_url(seed, width, height):
    return f"https://picsum.photos/seed/{slugify(seed)}/{width}/{height}"


class Command(BaseCommand):
    help = "Populates the database with realistic demo data for local development"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        self._create_users()
        self._create_restaurants_and_menus()

        self.stdout.write(self.style.SUCCESS("\nDatabase successfully seeded!"))

    def _create_users(self):
        self.stdout.write(self.style.HTTP_INFO("\nCreating users..."))

        admin_email = "admin@example.com"
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                username="admin",
                password="password123",
                role="ADMIN",
            )
            self.stdout.write(self.style.SUCCESS(f" Created Admin: {admin_email}"))
        else:
            admin = User.objects.get(email=admin_email)
            if admin.role != "ADMIN":
                admin.role = "ADMIN"
                admin.save(update_fields=["role"])
            self.stdout.write(f" Admin {admin_email} already exists.")

        client_email = "client@example.com"
        client_user, created = User.objects.get_or_create(
            email=client_email,
            defaults={"username": "client_user", "role": "CLIENT"},
        )
        if created:
            client_user.set_password("password123")
            client_user.save()
            self.stdout.write(self.style.SUCCESS(f" Created Client: {client_email}"))
        else:
            if client_user.role != "CLIENT":
                client_user.role = "CLIENT"
                client_user.save(update_fields=["role"])
            self.stdout.write(f" Client {client_email} already exists.")

        courier_email = "courier@example.com"
        courier_user, created = User.objects.get_or_create(
            email=courier_email,
            defaults={"username": "courier_user", "role": "COURIER"},
        )
        if created:
            courier_user.set_password("password123")
            courier_user.save()
            self.stdout.write(self.style.SUCCESS(f" Created Courier: {courier_email}"))
        else:
            if courier_user.role != "COURIER":
                courier_user.role = "COURIER"
                courier_user.save(update_fields=["role"])
            self.stdout.write(f" Courier {courier_email} already exists.")

    def _create_restaurants_and_menus(self):
        self.stdout.write(
            self.style.HTTP_INFO("\nCreating cuisines, restaurants, categories, and menu items...")
        )

        restaurants_data = [
            {
                "name": "Pizza Paradise",
                "cuisine": "Italian",
                "description": "Hand-stretched pizzas, sides, and desserts.",
                "image_url": _image_url("pizza-paradise", 800, 500),
                "address": "101 Main Street, New York, NY",
                "latitude": Decimal("40.712776"),
                "longitude": Decimal("-74.005974"),
                "rating": Decimal("4.70"),
                "delivery_time": 30,
                "items": {
                    "Pizza": [
                        ("Margherita", "Classic tomato, mozzarella, and basil.", Decimal("12.99")),
                        ("Pepperoni", "Pepperoni with house tomato sauce.", Decimal("14.99")),
                        ("BBQ Chicken", "BBQ chicken with red onion.", Decimal("16.99")),
                        ("Hawaiian", "Ham, pineapple, and mozzarella.", Decimal("15.50")),
                    ],
                    "Sides": [
                        ("Garlic Bread", "Toasted bread with garlic butter.", Decimal("4.99")),
                        ("Mozzarella Sticks", "Crispy fried mozzarella.", Decimal("6.99")),
                        ("Chicken Wings", "Spicy wings with ranch dip.", Decimal("8.99")),
                    ],
                    "Drinks": [
                        ("Coca Cola", "330ml can.", Decimal("2.50")),
                        ("Sprite", "330ml can.", Decimal("2.50")),
                        ("Water", "Still bottled water.", Decimal("1.50")),
                    ],
                    "Desserts": [
                        ("Tiramisu", "Coffee-flavored Italian dessert.", Decimal("5.99")),
                        ("Cheesecake", "Creamy baked cheesecake.", Decimal("6.50")),
                    ],
                },
            },
            {
                "name": "Burger Joint",
                "cuisine": "American",
                "description": "Classic burgers, fries, and milkshakes.",
                "image_url": _image_url("burger-joint", 800, 500),
                "address": "202 Market Street, Chicago, IL",
                "latitude": Decimal("41.878113"),
                "longitude": Decimal("-87.629799"),
                "rating": Decimal("4.50"),
                "delivery_time": 25,
                "items": {
                    "Burgers": [
                        ("Classic Cheeseburger", "Beef patty with cheddar and pickles.", Decimal("9.99")),
                        ("Bacon Double", "Double beef, bacon, cheddar, and sauce.", Decimal("13.99")),
                        ("Veggie Burger", "Plant-based patty with lettuce and tomato.", Decimal("10.99")),
                    ],
                    "Sides": [
                        ("French Fries", "Golden salted fries.", Decimal("3.99")),
                        ("Onion Rings", "Beer-battered onion rings.", Decimal("4.99")),
                        ("Sweet Potato Fries", "Sweet potato fries with dip.", Decimal("4.50")),
                    ],
                    "Drinks": [
                        ("Iced Tea", "Fresh brewed iced tea.", Decimal("2.00")),
                        ("Lemonade", "House lemonade.", Decimal("2.50")),
                    ],
                    "Shakes": [
                        ("Vanilla Shake", "Classic vanilla milkshake.", Decimal("5.00")),
                        ("Chocolate Shake", "Rich chocolate milkshake.", Decimal("5.00")),
                        ("Strawberry Shake", "Strawberry milkshake.", Decimal("5.00")),
                    ],
                },
            },
            {
                "name": "Sushi World",
                "cuisine": "Japanese",
                "description": "Fresh sushi rolls, nigiri, and Japanese snacks.",
                "image_url": _image_url("sushi-world", 800, 500),
                "address": "303 Harbor Road, San Francisco, CA",
                "latitude": Decimal("37.774929"),
                "longitude": Decimal("-122.419418"),
                "rating": Decimal("4.90"),
                "delivery_time": 35,
                "items": {
                    "Sushi Rolls": [
                        ("California Roll", "Crab, avocado, and cucumber.", Decimal("6.99")),
                        ("Spicy Tuna Roll", "Tuna with spicy mayo.", Decimal("8.99")),
                        ("Dragon Roll", "Eel, cucumber, and avocado.", Decimal("12.99")),
                        ("Rainbow Roll", "California roll topped with assorted fish.", Decimal("14.99")),
                    ],
                    "Nigiri": [
                        ("Salmon Nigiri", "Two pieces of salmon nigiri.", Decimal("5.99")),
                        ("Tuna Nigiri", "Two pieces of tuna nigiri.", Decimal("6.50")),
                        ("Eel Nigiri", "Two pieces of eel nigiri.", Decimal("7.00")),
                    ],
                    "Appetizers": [
                        ("Edamame", "Steamed salted edamame.", Decimal("4.50")),
                        ("Miso Soup", "Traditional miso soup.", Decimal("3.50")),
                        ("Gyoza", "Pan-fried dumplings.", Decimal("5.99")),
                    ],
                    "Drinks": [
                        ("Green Tea", "Hot green tea.", Decimal("2.00")),
                        ("Asahi Beer", "Japanese lager.", Decimal("4.50")),
                        ("Sake", "Warm sake.", Decimal("8.00")),
                    ],
                },
            },
        ]

        created_restaurants = 0
        created_cuisines = 0
        created_categories = 0
        created_items = 0

        for restaurant_data in restaurants_data:
            cuisine, cuisine_created = Cuisine.objects.get_or_create(
                name=restaurant_data["cuisine"]
            )
            if cuisine_created:
                created_cuisines += 1

            restaurant, restaurant_created = Restaurant.objects.get_or_create(
                name=restaurant_data["name"],
                defaults={
                    "description": restaurant_data["description"],
                    "image_url": restaurant_data["image_url"],
                    "address": restaurant_data["address"],
                    "latitude": restaurant_data["latitude"],
                    "longitude": restaurant_data["longitude"],
                    "cuisine": cuisine,
                    "rating": restaurant_data["rating"],
                    "delivery_time": restaurant_data["delivery_time"],
                },
            )
            if restaurant_created:
                created_restaurants += 1
            else:
                restaurant.description = restaurant_data["description"]
                restaurant.image_url = restaurant_data["image_url"]
                restaurant.address = restaurant_data["address"]
                restaurant.latitude = restaurant_data["latitude"]
                restaurant.longitude = restaurant_data["longitude"]
                restaurant.cuisine = cuisine
                restaurant.rating = restaurant_data["rating"]
                restaurant.delivery_time = restaurant_data["delivery_time"]
                restaurant.save(
                    update_fields=[
                        "description",
                        "image_url",
                        "address",
                        "latitude",
                        "longitude",
                        "cuisine",
                        "rating",
                        "delivery_time",
                    ]
                )

            OpeningHours.objects.update_or_create(
                restaurant=restaurant,
                day_type="weekday",
                defaults={"opens_at": "09:00", "closes_at": "22:00"},
            )
            OpeningHours.objects.update_or_create(
                restaurant=restaurant,
                day_type="weekend",
                defaults={"opens_at": "10:00", "closes_at": "23:00"},
            )

            for category_name, menu_items in restaurant_data["items"].items():
                category, category_created = Category.objects.get_or_create(name=category_name)
                if category_created:
                    created_categories += 1

                for item_name, item_description, item_price in menu_items:
                    is_available = item_name not in {"Chicken Wings", "Strawberry Shake", "Sake"}
                    item, item_created = MenuItem.objects.update_or_create(
                        restaurant=restaurant,
                        name=item_name,
                        defaults={
                            "category": category,
                            "description": item_description,
                            "price": item_price,
                            "image_url": _image_url(
                                f"{restaurant.name}-{item_name}", 400, 300
                            ),
                            "is_available": is_available,
                            "unavailable_reason": "" if is_available else "Temporarily sold out",
                            "is_vegetarian": item_name in {
                                "Margherita", "Garlic Bread", "French Fries",
                                "Onion Rings", "Edamame", "Miso Soup",
                            },
                            "is_vegan": item_name in {"French Fries", "Edamame"},
                            "calories": 120 + len(item_name) * 10,
                        },
                    )
                    if item.image:
                        item.image = None
                        item.save(update_fields=["image"])
                    if item_created:
                        created_items += 1

        self.stdout.write(
            self.style.SUCCESS(
                f" Successfully ensured {len(restaurants_data)} restaurants are seeded."
            )
        )
        self.stdout.write(f"  + Created {created_cuisines} new cuisines")
        self.stdout.write(f"  + Created {created_restaurants} new restaurants")
        self.stdout.write(f"  + Created {created_categories} new categories")
        self.stdout.write(f"  + Created {created_items} new menu items")
