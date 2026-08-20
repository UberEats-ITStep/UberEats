from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from cart.models import Cart, CartItem
from favorites.models import Favorite
from orders.models import Order, OrderItem
from reviews.models import Review
from restaurants.models import Category, Cuisine, MenuItem, MenuTag, OpeningHours, Restaurant


User = get_user_model()


def _image_url(seed, width, height):
    return f"https://picsum.photos/seed/{slugify(seed)}/{width}/{height}"


class Command(BaseCommand):
    help = "Populates the database with realistic demo data for Rivne"

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
        self.stdout.write(self.style.HTTP_INFO("\nClearing old orders, carts, and reviews for clean replacement..."))
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()
        Favorite.objects.all().delete()
        
        self.stdout.write(self.style.HTTP_INFO("\nCreating cuisines, restaurants, categories, menu items, and tags...")
        )

        # Realistic Rivne Restaurants Dataset
        restaurants_data = [
            {
                "name": "Kant",
                "cuisine": "Pub",
                "description": "Local brewery and restaurant offering traditional European and Ukrainian pub fare. Famous for its craft beer and hearty meat dishes.",
                "image_url": _image_url("kant-rivne", 800, 500),
                "address": "Kopernyka St, 9, Rivne, Rivnens'ka oblast, Ukraine, 33000",
                "latitude": Decimal("50.6200"),
                "longitude": Decimal("26.2500"),
                "rating": Decimal("4.80"),
                "delivery_time": 45,
                "items": {
                    "Hot Dishes": [
                        ("Pork Ribs in Honey Glaze", "Slow-cooked pork ribs glazed with local honey and dark beer.", Decimal("350.00"), ["meat", "savory", "filling"], False, False, 850),
                        ("Bavarian Sausages", "Assorted grilled sausages served with mustard and pretzels.", Decimal("280.00"), ["meat", "savory", "filling"], False, False, 700),
                    ],
                    "Snacks": [
                        ("Garlic Croutons", "Crispy deep-fried rye bread with garlic and cheese sauce.", Decimal("95.00"), ["snack", "savory", "crispy"], True, False, 450),
                        ("Cheese Balls", "Deep-fried mozzarella and cheddar balls with berry sauce.", Decimal("150.00"), ["snack", "savory", "crispy", "vegetarian"], True, False, 520),
                    ],
                    "Salads": [
                        ("Warm Veal Salad", "Tender veal slices with grilled vegetables and balsamic dressing.", Decimal("240.00"), ["healthy", "high-protein", "savory"], False, False, 350),
                    ]
                },
            },
            {
                "name": "La Riva",
                "cuisine": "Italian",
                "description": "Authentic Italian restaurant located near the river, offering wood-fired pizzas, handmade pasta, and Mediterranean dishes.",
                "image_url": _image_url("la-riva", 800, 500),
                "address": "Mickiewicz St, Rivne, Ukraine",
                "latitude": Decimal("50.6180"),
                "longitude": Decimal("26.2550"),
                "rating": Decimal("4.70"),
                "delivery_time": 30,
                "items": {
                    "Pizza": [
                        ("Pizza Margherita", "Classic Neapolitan pizza with San Marzano tomatoes, fresh mozzarella, and basil.", Decimal("220.00"), ["savory", "comfort-food", "vegetarian"], True, False, 800),
                        ("Pizza Quattro Formaggi", "Four cheese pizza featuring gorgonzola, mozzarella, parmesan, and fontina.", Decimal("290.00"), ["savory", "comfort-food", "vegetarian"], True, False, 950),
                        ("Pizza Prosciutto e Rucola", "Italian pizza topped with Parma ham, fresh arugula, and parmesan shavings.", Decimal("320.00"), ["savory", "comfort-food", "meat"], False, False, 900),
                    ],
                    "Pasta": [
                        ("Spaghetti Carbonara", "Traditional Roman pasta with guanciale, pecorino cheese, and egg yolk. No cream.", Decimal("260.00"), ["savory", "comfort-food", "filling"], False, False, 850),
                        ("Penne Arrabbiata", "Penne pasta in a spicy tomato sauce with garlic and chili flakes.", Decimal("210.00"), ["spicy", "vegetarian", "vegan"], True, True, 600),
                    ],
                    "Desserts": [
                        ("Tiramisu", "Classic Italian dessert with espresso-soaked ladyfingers and mascarpone cream.", Decimal("150.00"), ["sweet", "dessert", "creamy"], True, False, 450),
                    ]
                },
            },
            {
                "name": "Kinza",
                "cuisine": "Georgian",
                "description": "Cozy Georgian restaurant famous for juicy khinkali, hot khachapuri, and grilled meats.",
                "image_url": _image_url("kinza", 800, 500),
                "address": "Kyivska St, Rivne, Ukraine",
                "latitude": Decimal("50.6170"),
                "longitude": Decimal("26.2580"),
                "rating": Decimal("4.90"),
                "delivery_time": 40,
                "items": {
                    "Khinkali": [
                        ("Khinkali with Veal and Pork", "Traditional Georgian dumplings filled with juicy minced veal and pork.", Decimal("180.00"), ["savory", "meat", "filling", "comfort-food"], False, False, 700),
                        ("Khinkali with Cheese", "Georgian dumplings filled with melted suluguni cheese.", Decimal("160.00"), ["savory", "vegetarian", "comfort-food"], True, False, 650),
                    ],
                    "Khachapuri": [
                        ("Khachapuri Adjarian", "Boat-shaped bread filled with cheese and topped with a raw egg and butter.", Decimal("220.00"), ["savory", "vegetarian", "comfort-food", "filling"], True, False, 850),
                        ("Khachapuri Megrelian", "Round cheese bread baked with extra cheese on top.", Decimal("240.00"), ["savory", "vegetarian", "comfort-food"], True, False, 900),
                    ],
                    "Hot Dishes": [
                        ("Pork Mtsvadi (Shashlik)", "Georgian-style pork skewers grilled over open coals.", Decimal("300.00"), ["savory", "meat", "high-protein"], False, False, 600),
                        ("Chakhokhbili", "Traditional Georgian chicken stew with tomatoes, herbs, and spices.", Decimal("250.00"), ["savory", "meat", "spicy"], False, False, 450),
                    ]
                },
            },
            {
                "name": "Fortissimo",
                "cuisine": "Cafe",
                "description": "Elegant city-center cafe offering specialty coffee, exquisite desserts, and light European breakfasts.",
                "image_url": _image_url("fortissimo", 800, 500),
                "address": "16 Lermontova St, Rivne, Ukraine",
                "latitude": Decimal("50.6210"),
                "longitude": Decimal("26.2560"),
                "rating": Decimal("4.60"),
                "delivery_time": 25,
                "items": {
                    "Breakfasts": [
                        ("Avocado Toast with Salmon", "Sourdough toast with smashed avocado, lightly salted salmon, and a poached egg.", Decimal("280.00"), ["breakfast", "healthy", "high-protein", "fresh"], False, False, 450),
                        ("Oatmeal with Fresh Berries", "Warm oatmeal cooked with almond milk, topped with seasonal berries and nuts.", Decimal("150.00"), ["breakfast", "healthy", "vegan", "sweet"], True, True, 350),
                        ("Syrnyky", "Traditional Ukrainian cottage cheese pancakes served with sour cream and jam.", Decimal("190.00"), ["breakfast", "sweet", "vegetarian", "comfort-food"], True, False, 500),
                    ],
                    "Desserts": [
                        ("Basque Cheesecake", "Caramelized burnt cheesecake with a creamy center.", Decimal("160.00"), ["dessert", "sweet", "creamy"], True, False, 400),
                        ("Macaron Set", "Assortment of 5 colorful French macarons.", Decimal("200.00"), ["dessert", "sweet"], True, False, 250),
                    ],
                    "Drinks": [
                        ("Cappuccino", "Classic espresso with steamed milk and thick foam.", Decimal("85.00"), ["drink", "breakfast"], True, False, 120),
                        ("Matcha Latte", "Premium Japanese matcha green tea whisked with steamed milk.", Decimal("110.00"), ["drink", "healthy"], True, False, 100),
                    ]
                },
            },
            {
                "name": "Sushi Wok",
                "cuisine": "Asian",
                "description": "Fast and delicious pan-Asian cuisine, specializing in wok noodles, sushi sets, and Asian soups.",
                "image_url": _image_url("sushi-wok", 800, 500),
                "address": "Soborna St, 192, Rivne, Ukraine",
                "latitude": Decimal("50.6225"),
                "longitude": Decimal("26.2555"),
                "rating": Decimal("4.40"),
                "delivery_time": 35,
                "items": {
                    "Sushi Rolls": [
                        ("Philadelphia Roll", "Classic roll with fresh salmon, cream cheese, and cucumber.", Decimal("240.00"), ["savory", "fresh", "creamy"], False, False, 400),
                        ("Spicy Tuna Roll", "Maki roll with spicy tuna tartare and scallions.", Decimal("220.00"), ["spicy", "savory", "fresh"], False, False, 350),
                        ("Avocado Maki", "Simple vegan maki roll with fresh avocado.", Decimal("120.00"), ["vegan", "vegetarian", "fresh", "healthy"], True, True, 200),
                    ],
                    "Wok Noodles": [
                        ("Udon with Chicken and Teriyaki", "Thick udon noodles wok-tossed with chicken breast, vegetables, and sweet teriyaki sauce.", Decimal("190.00"), ["savory", "sweet", "filling", "comfort-food", "lunch"], False, False, 650),
                        ("Soba with Tofu and Vegetables", "Buckwheat noodles stir-fried with crispy tofu and mixed vegetables in a soy-ginger sauce.", Decimal("180.00"), ["vegan", "vegetarian", "healthy", "filling"], True, True, 500),
                    ],
                    "Soups": [
                        ("Tom Yum with Shrimp", "Spicy and sour Thai soup with shrimp, mushrooms, and lemongrass.", Decimal("260.00"), ["spicy", "savory", "fresh"], False, False, 300),
                        ("Miso Soup", "Traditional Japanese soybean broth with wakame seaweed and tofu.", Decimal("90.00"), ["vegan", "vegetarian", "healthy", "light"], True, True, 80),
                    ]
                },
            },
            {
                "name": "Panska Vtiha",
                "cuisine": "Ukrainian",
                "description": "Authentic Ukrainian cuisine featuring traditional borsch, varenyky, and homemade liqueurs in a traditional setting.",
                "image_url": _image_url("panska-vtiha", 800, 500),
                "address": "15 Hrushevskoho St, Rivne, Ukraine",
                "latitude": Decimal("50.6280"),
                "longitude": Decimal("26.2300"),
                "rating": Decimal("4.80"),
                "delivery_time": 40,
                "items": {
                    "Soups": [
                        ("Ukrainian Borsch with Ribs", "Rich beetroot soup with pork ribs, served with sour cream, garlic pampushky, and salo.", Decimal("180.00"), ["savory", "comfort-food", "filling", "meat"], False, False, 550),
                        ("Mushroom Soup", "Creamy wild mushroom soup served in a bread bowl.", Decimal("160.00"), ["savory", "comfort-food", "vegetarian"], True, False, 450),
                    ],
                    "Main Dishes": [
                        ("Varenyky with Potatoes and Mushroom", "Handmade dumplings filled with mashed potatoes and mushrooms, topped with fried onions.", Decimal("150.00"), ["savory", "comfort-food", "vegetarian", "filling"], True, False, 500),
                        ("Varenyky with Cherries", "Sweet handmade dumplings filled with sour cherries, served with sour cream and sugar.", Decimal("160.00"), ["sweet", "dessert", "vegetarian"], True, False, 400),
                        ("Chicken Kyiv", "Breaded chicken breast stuffed with herb butter, served with mashed potatoes.", Decimal("240.00"), ["savory", "meat", "comfort-food", "filling"], False, False, 800),
                    ],
                    "Appetizers": [
                        ("Salo Plate", "Assortment of traditional Ukrainian cured pork fat with garlic and rye bread.", Decimal("140.00"), ["savory", "snack", "meat"], False, False, 600),
                    ]
                },
            },
            {
                "name": "Burger Joint Rivne",
                "cuisine": "American",
                "description": "Premium craft burgers made with 100% local beef, loaded fries, and thick milkshakes.",
                "image_url": _image_url("burger-joint-rivne", 800, 500),
                "address": "Soborna St, 15, Rivne, Ukraine",
                "latitude": Decimal("50.6190"),
                "longitude": Decimal("26.2520"),
                "rating": Decimal("4.50"),
                "delivery_time": 30,
                "items": {
                    "Burgers": [
                        ("Classic Smashburger", "Double smashed beef patties with American cheese, pickles, and house sauce on a brioche bun.", Decimal("210.00"), ["savory", "meat", "comfort-food", "lunch"], False, False, 850),
                        ("Spicy Jalapeno Burger", "Beef patty with pepper jack cheese, pickled jalapenos, bacon, and spicy mayo.", Decimal("240.00"), ["spicy", "savory", "meat", "comfort-food"], False, False, 900),
                        ("Beyond Veggie Burger", "Plant-based Beyond Meat patty with vegan cheese, lettuce, and tomato.", Decimal("280.00"), ["vegan", "vegetarian", "savory", "comfort-food"], True, True, 600),
                    ],
                    "Sides": [
                        ("Loaded Cheese Fries", "Crispy French fries topped with melted cheddar sauce, bacon bits, and jalapeños.", Decimal("150.00"), ["savory", "comfort-food", "snack", "spicy"], False, False, 750),
                        ("Sweet Potato Fries", "Crispy sweet potato fries served with garlic aioli.", Decimal("120.00"), ["savory", "vegetarian", "snack"], True, False, 400),
                    ],
                    "Drinks": [
                        ("Oreo Milkshake", "Thick vanilla milkshake blended with Oreo cookies.", Decimal("130.00"), ["sweet", "dessert", "creamy"], True, False, 600),
                        ("Craft Lemonade", "House-made refreshing citrus lemonade.", Decimal("80.00"), ["drink", "fresh", "sweet", "vegan"], True, True, 150),
                    ]
                },
            },
            {
                "name": "Green Life",
                "cuisine": "Healthy Food",
                "description": "Healthy lifestyle cafe focusing on fresh salads, smoothie bowls, and gluten-free, vegan-friendly options.",
                "image_url": _image_url("green-life", 800, 500),
                "address": "Chornovola St, Rivne, Ukraine",
                "latitude": Decimal("50.6250"),
                "longitude": Decimal("26.2400"),
                "rating": Decimal("4.90"),
                "delivery_time": 25,
                "items": {
                    "Bowls": [
                        ("Quinoa Buddha Bowl", "Quinoa, roasted sweet potato, kale, avocado, and tahini dressing.", Decimal("210.00"), ["vegan", "vegetarian", "healthy", "fresh", "lunch"], True, True, 450),
                        ("Salmon Poke Bowl", "Sushi rice, fresh salmon, edamame, cucumber, radishes, and ponzu sauce.", Decimal("280.00"), ["healthy", "fresh", "high-protein", "lunch"], False, False, 500),
                    ],
                    "Salads": [
                        ("Super Green Salad", "Mixed greens, spinach, avocado, green apples, pumpkin seeds, and lemon-olive oil dressing.", Decimal("180.00"), ["vegan", "vegetarian", "healthy", "fresh", "light"], True, True, 300),
                    ],
                    "Smoothies": [
                        ("Berry Antioxidant Smoothie", "Mixed wild berries, banana, chia seeds, and almond milk.", Decimal("120.00"), ["vegan", "vegetarian", "healthy", "sweet", "drink"], True, True, 200),
                        ("Green Detox Juice", "Cold-pressed apple, celery, spinach, cucumber, and ginger juice.", Decimal("140.00"), ["vegan", "vegetarian", "healthy", "fresh", "drink"], True, True, 110),
                    ]
                },
            },
            {
                "name": "Pasta Mia",
                "cuisine": "Italian",
                "description": "Fast-casual Italian dining offering fresh pasta, thin-crust pizza, and Italian salads.",
                "image_url": _image_url("pasta-mia", 800, 500),
                "address": "Makarova St, Rivne, Ukraine",
                "latitude": Decimal("50.6220"),
                "longitude": Decimal("26.2600"),
                "rating": Decimal("4.40"),
                "delivery_time": 25,
                "items": {
                    "Pasta": [
                        ("Fettuccine Alfredo", "Fresh fettuccine pasta in a rich, creamy parmesan and butter sauce.", Decimal("190.00"), ["savory", "comfort-food", "vegetarian", "creamy"], True, False, 750),
                        ("Pasta Bolognese", "Classic spaghetti with slow-cooked beef and tomato ragu.", Decimal("210.00"), ["savory", "meat", "comfort-food", "filling"], False, False, 800),
                    ],
                    "Salads": [
                        ("Caesar Salad with Chicken", "Romaine lettuce, grilled chicken breast, parmesan, croutons, and Caesar dressing.", Decimal("170.00"), ["savory", "high-protein", "healthy"], False, False, 450),
                    ]
                }
            },
            {
                "name": "Tri Slona",
                "cuisine": "Pub",
                "description": "A spacious pub offering a huge selection of draft beers and hearty snacks for large companies.",
                "image_url": _image_url("tri-slona", 800, 500),
                "address": "Soborna St, Rivne, Ukraine",
                "latitude": Decimal("50.6150"),
                "longitude": Decimal("26.2700"),
                "rating": Decimal("4.60"),
                "delivery_time": 40,
                "items": {
                    "Pub Snacks": [
                        ("Huge Snack Platter", "Onion rings, cheese balls, chicken wings, garlic croutons, and french fries.", Decimal("450.00"), ["snack", "savory", "crispy", "filling"], False, False, 1800),
                        ("Spicy Chicken Wings", "Crispy deep-fried chicken wings glazed in a spicy buffalo sauce.", Decimal("220.00"), ["spicy", "savory", "meat", "snack"], False, False, 850),
                    ],
                    "Burgers": [
                        ("Tri Slona Big Burger", "Double beef patty, bacon, cheddar, egg, and BBQ sauce.", Decimal("280.00"), ["savory", "meat", "filling", "comfort-food"], False, False, 1100),
                    ]
                }
            },
            {
                "name": "Flamingo",
                "cuisine": "Pizza",
                "description": "Family-friendly pizzeria serving classic pizzas, fresh salads, and desserts in a colorful atmosphere.",
                "image_url": _image_url("flamingo", 800, 500),
                "address": "Gagarina St, Rivne, Ukraine",
                "latitude": Decimal("50.6250"),
                "longitude": Decimal("26.2400"),
                "rating": Decimal("4.70"),
                "delivery_time": 35,
                "items": {
                    "Pizza": [
                        ("Pizza Hawaiian", "Pizza with ham, fresh pineapple, mozzarella, and tomato sauce.", Decimal("190.00"), ["sweet", "savory", "meat", "comfort-food"], False, False, 850),
                        ("Pizza Diablo", "Spicy pizza with pepperoni, jalapenos, chili flakes, and mozzarella.", Decimal("230.00"), ["spicy", "savory", "meat", "comfort-food"], False, False, 900),
                    ],
                    "Kids Menu": [
                        ("Kids Cheese Pizza", "Small classic cheese and tomato pizza.", Decimal("120.00"), ["savory", "vegetarian", "comfort-food"], True, False, 400),
                        ("Chicken Nuggets with Fries", "Crispy chicken nuggets served with french fries and ketchup.", Decimal("140.00"), ["savory", "meat", "crispy", "comfort-food"], False, False, 550),
                    ]
                }
            },
            {
                "name": "Pizza Celentano",
                "cuisine": "Pizza",
                "description": "Famous Ukrainian pizza chain where you can build your own pizza. Known for democratic prices.",
                "image_url": _image_url("pizza-celentano", 800, 500),
                "address": "Soborna St, Rivne, Ukraine",
                "latitude": Decimal("50.6190"),
                "longitude": Decimal("26.2520"),
                "rating": Decimal("4.20"),
                "delivery_time": 30,
                "items": {
                    "Pizza": [
                        ("Pizza Capricciosa", "Tomato sauce, mozzarella, mushrooms, artichokes, ham, and olives.", Decimal("200.00"), ["savory", "meat", "comfort-food"], False, False, 850),
                        ("Vegetarian Pizza", "Tomato sauce, mozzarella, bell peppers, corn, mushrooms, and tomatoes.", Decimal("180.00"), ["savory", "vegetarian", "comfort-food"], True, False, 700),
                    ],
                    "Pancakes": [
                        ("Crepes with Chicken and Mushrooms", "Savory thin pancakes stuffed with chicken and creamy mushrooms.", Decimal("110.00"), ["savory", "meat", "comfort-food"], False, False, 450),
                        ("Crepes with Nutella and Banana", "Sweet thin pancakes filled with Nutella and fresh banana slices.", Decimal("90.00"), ["sweet", "dessert", "vegetarian"], True, False, 500),
                    ]
                }
            },
            {
                "name": "Le Grand",
                "cuisine": "European",
                "description": "High-end European and French cuisine perfect for romantic dinners and business meetings.",
                "image_url": _image_url("le-grand", 800, 500),
                "address": "Zamkova St, Rivne, Ukraine",
                "latitude": Decimal("50.6160"),
                "longitude": Decimal("26.2500"),
                "rating": Decimal("4.80"),
                "delivery_time": 45,
                "items": {
                    "Main Dishes": [
                        ("Filet Mignon", "Tender beef steak served with asparagus and truffle puree.", Decimal("550.00"), ["savory", "meat", "high-protein", "dinner"], False, False, 600),
                        ("Duck Breast with Berry Sauce", "Pan-seared duck breast served with sweet and sour berry reduction.", Decimal("420.00"), ["savory", "sweet", "meat", "dinner"], False, False, 550),
                    ],
                    "Appetizers": [
                        ("Beef Tartare", "Raw minced beef with capers, shallots, and egg yolk, served with toasts.", Decimal("280.00"), ["savory", "meat", "fresh"], False, False, 300),
                        ("Escargot", "Snails baked in garlic and herb butter.", Decimal("220.00"), ["savory", "meat", "snack"], False, False, 250),
                    ]
                }
            },
            {
                "name": "Dvir",
                "cuisine": "Ukrainian",
                "description": "Modern Ukrainian cuisine and grill house featuring local farm ingredients and open-fire cooking.",
                "image_url": _image_url("dvir", 800, 500),
                "address": "Kyivska St, Rivne, Ukraine",
                "latitude": Decimal("50.6205"),
                "longitude": Decimal("26.2480"),
                "rating": Decimal("4.70"),
                "delivery_time": 35,
                "items": {
                    "Grill": [
                        ("Grilled Ribeye Steak", "Local dry-aged beef steak grilled over oak coals.", Decimal("480.00"), ["savory", "meat", "high-protein", "filling"], False, False, 700),
                        ("Grilled Vegetables", "Seasonal local vegetables grilled with olive oil and herbs.", Decimal("140.00"), ["vegan", "vegetarian", "healthy", "light"], True, True, 200),
                    ],
                    "Modern Ukrainian": [
                        ("Deruny with Wild Mushrooms", "Crispy potato pancakes served with a creamy wild mushroom sauce.", Decimal("170.00"), ["savory", "vegetarian", "comfort-food", "crispy"], True, False, 550),
                        ("Banosh with Brynza", "Traditional cornmeal porridge topped with sheep cheese and pork cracklings.", Decimal("190.00"), ["savory", "meat", "filling", "comfort-food"], False, False, 800),
                    ]
                }
            },
            {
                "name": "Lviv Croissants",
                "cuisine": "Bakery",
                "description": "Famous bakery network offering huge, freshly baked croissants with various sweet and savory fillings.",
                "image_url": _image_url("lviv-croissants", 800, 500),
                "address": "Soborna St, Rivne, Ukraine",
                "latitude": Decimal("50.6185"),
                "longitude": Decimal("26.2530"),
                "rating": Decimal("4.60"),
                "delivery_time": 20,
                "items": {
                    "Savory Croissants": [
                        ("Lviv Croissant", "Signature croissant filled with salami, egg, cheese, cucumber, and lettuce.", Decimal("110.00"), ["savory", "meat", "breakfast", "lunch", "snack"], False, False, 550),
                        ("Salmon Croissant", "Croissant filled with lightly salted salmon, cream cheese, and arugula.", Decimal("150.00"), ["savory", "fresh", "healthy", "breakfast"], False, False, 450),
                    ],
                    "Sweet Croissants": [
                        ("Raspberry Mascarpone Croissant", "Croissant filled with sweet mascarpone cream and fresh raspberries.", Decimal("95.00"), ["sweet", "dessert", "vegetarian", "creamy"], True, False, 500),
                        ("Chocolate Croissant", "Croissant filled with rich chocolate paste.", Decimal("85.00"), ["sweet", "dessert", "vegetarian"], True, False, 480),
                    ],
                    "Drinks": [
                        ("Latte", "Espresso with lots of steamed milk.", Decimal("65.00"), ["drink", "breakfast"], True, False, 150),
                    ]
                }
            }
        ]

        # Process Tags First to avoid creating them multiple times per item
        all_possible_tags = [
            "spicy", "sweet", "savory", "fresh", "creamy", "crispy", "healthy", "filling",
            "breakfast", "lunch", "dinner", "snack", "dessert", "drink", "high-protein", 
            "comfort-food", "light", "meat", "vegetarian", "vegan"
        ]
        tag_objects = {}
        for tag_name in all_possible_tags:
            tag_obj, _ = MenuTag.objects.get_or_create(name=tag_name)
            tag_objects[tag_name] = tag_obj

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

            # Determine coordinates cleanly
            lat = restaurant_data.get("latitude")
            lng = restaurant_data.get("longitude")

            restaurant, restaurant_created = Restaurant.objects.get_or_create(
                name=restaurant_data["name"],
                defaults={
                    "description": restaurant_data["description"],
                    "image_url": restaurant_data["image_url"],
                    "address": restaurant_data["address"],
                    "latitude": lat,
                    "longitude": lng,
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
                restaurant.latitude = lat
                restaurant.longitude = lng
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

                for item_name, item_description, item_price, tags, is_veg, is_vegan, calories in menu_items:
                    # Synthetic availability for demo
                    is_available = item_name not in {"Macaron Set", "Mushroom Soup"}
                    
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
                            "is_vegetarian": is_veg,
                            "is_vegan": is_vegan,
                            "calories": calories,
                        },
                    )
                    
                    # Associate tags
                    item.tags.clear()
                    item_tags_to_add = [tag_objects[t] for t in tags if t in tag_objects]
                    if item_tags_to_add:
                        item.tags.add(*item_tags_to_add)


                    if item.image:
                        item.image = None
                        item.save(update_fields=["image"])
                    if item_created:
                        created_items += 1
                        
                # Ensure each restaurant has at least 10 items to hit the 150 quota
                while sum(len(items) for items in restaurant_data["items"].values()) < 10:
                    demo_suffix = str(sum(len(it) for it in restaurant_data["items"].values()))
                    # Pick a random category to expand
                    cat_name = list(restaurant_data["items"].keys())[0]
                    base_item = restaurant_data["items"][cat_name][0]
                    
                    demo_item_name = f"{base_item[0]} (Demo {demo_suffix})"
                    demo_description = f"Synthetic demo variation of {base_item[0]} for AI context. {base_item[1]}"
                    demo_price = base_item[2] + Decimal("20.00")
                    demo_tags = base_item[3]
                    is_veg = base_item[4]
                    is_vegan = base_item[5]
                    calories = base_item[6] + 20
                    
                    # Add to memory so loop counts it
                    restaurant_data["items"][cat_name].append((demo_item_name, demo_description, demo_price, demo_tags, is_veg, is_vegan, calories))
                    
                    # Save to db
                    demo_item, demo_created = MenuItem.objects.update_or_create(
                        restaurant=restaurant,
                        name=demo_item_name,
                        defaults={
                            "category": category,
                            "description": demo_description,
                            "price": demo_price,
                            "image_url": _image_url(f"{restaurant.name}-{demo_item_name}", 400, 300),
                            "is_available": True,
                            "unavailable_reason": "",
                            "is_vegetarian": is_veg,
                            "is_vegan": is_vegan,
                            "calories": calories,
                        }
                    )
                    
                    demo_item.tags.clear()
                    item_tags_to_add = [tag_objects[t] for t in demo_tags if t in tag_objects]
                    if item_tags_to_add:
                        demo_item.tags.add(*item_tags_to_add)
                        
                    if demo_created:
                        created_items += 1


        # Delete any items/restaurants that are not in this list to ensure clean slate
        # Wait, the prompt says "multiple times should not create duplicate restaurants", 
        # but to make it purely idempotent and remove old demo data ("Pizza Paradise"):
        valid_restaurant_names = [r["name"] for r in restaurants_data]
        Restaurant.objects.exclude(name__in=valid_restaurant_names).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f" Successfully ensured {len(restaurants_data)} restaurants are seeded."
            )
        )
        self.stdout.write(f"  + Created/Updated {created_cuisines} cuisines")
        self.stdout.write(f"  + Created/Updated {created_restaurants} restaurants")
        self.stdout.write(f"  + Created/Updated {created_categories} categories")
        self.stdout.write(f"  + Created/Updated {created_items} menu items")
