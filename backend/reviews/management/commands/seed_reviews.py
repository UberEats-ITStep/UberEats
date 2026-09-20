import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, MenuItem
from orders.models import Order, OrderItem
from reviews.models import Review

User = get_user_model()

# Deterministic Demo Users
DEMO_USER_DOMAIN = "biteup.demo"
DEMO_USER_PREFIX = "demo_reviewer_"
DEMO_USER_COUNT = 15

UKRAINIAN_NAMES = [
    "Oleksandr", "Andrii", "Artem", "Bohdan", "Danylo", "Denys", "Dmytro", "Ivan", 
    "Maksym", "Mykhailo", "Nazar", "Oleksii", "Pavlo", "Petro", "Roman", "Serhii", 
    "Taras", "Vadym", "Volodymyr", "Yaroslav", "Anastasiia", "Anna", "Bohdana", 
    "Daria", "Kateryna", "Khrystyna", "Liudmyla", "Mariia", "Marta", "Nataliia", 
    "Oksana", "Olena", "Polina", "Svitlana", "Tetiana", "Valentyna", "Viktoriia", 
    "Yana", "Yelyzaveta", "Yuliia", "Alina", "Diana", "Iryna", "Karina", "Lesia", 
    "Sofia", "Solomiia", "Veronika", "Vlada", "Zoriana"
]

TEMPLATES = {
    "Japanese": {
        5: [
            "The sushi was incredibly fresh. The rice was perfectly seasoned.",
            "Generous portions of sashimi, and the rolls were beautifully presented.",
            "Best tempura I've had in a while. Crisp and not greasy.",
            "Everything was perfect. The fish quality is top-notch."
        ],
        4: [
            "Really good sushi, but delivery took a bit longer.",
            "Fresh ingredients and good flavor. Portions were slightly small.",
            "Great rolls, well packed. Would order again."
        ],
        3: [
            "Average sushi. Nothing special, but okay for the price.",
            "The rice was a bit too dry, but the fish was fresh."
        ],
        2: [
            "Rolls fell apart easily. Disappointing presentation."
        ],
        1: [
            "Fish didn't taste very fresh. Not ordering again."
        ]
    },
    "Italian": {
        5: [
            "The pasta was perfectly al dente and the sauce was rich.",
            "Amazing wood-fired pizza with a perfect crust.",
            "Authentic Italian flavors. The tiramisu is a must-try!",
            "Hot, fresh, and delicious pizza. Highly recommend."
        ],
        4: [
            "Great pizza, though a bit too much cheese for my liking.",
            "Pasta was good, but the garlic bread was slightly burnt.",
            "Delicious food, came nicely packaged and warm."
        ],
        3: [
            "The pasta sauce lacked seasoning, but the pizza was decent.",
            "Average Italian food. A bit overpriced for the portion size."
        ],
        2: [
            "Pizza arrived cold and the crust was soggy."
        ],
        1: [
            "Terrible pasta, tasted like it was from a can."
        ]
    },
    "Ukrainian": {
        5: [
            "Incredible borscht! Just like my grandmother makes it.",
            "Varenyky were soft and stuffed perfectly. Delicious sour cream.",
            "Very authentic and hearty Ukrainian food. Generous portions.",
            "The chicken Kyiv was perfectly crispy on the outside."
        ],
        4: [
            "Good traditional food, but a bit too greasy.",
            "The borscht was great, though it needed more meat.",
            "Tasty varenyky, arrived hot."
        ],
        3: [
            "Decent food, but lacked some traditional flavor.",
            "Varenyky dough was a bit too thick."
        ],
        2: [
            "Borscht was watery and tasteless."
        ],
        1: [
            "Very poor quality. Did not taste authentic at all."
        ]
    },
    "Fast Food": {
        5: [
            "Best burger I've had in town. Juicy patty and fresh bun.",
            "Fries were crispy and the burger was perfectly cooked.",
            "Fast, delicious, and exactly what I craved. Great value.",
            "The sauce on the burger is incredible."
        ],
        4: [
            "Good burger, but the fries were a bit cold.",
            "Tasty and fast, but presentation was messy.",
            "Solid fast food option. Always consistent."
        ],
        3: [
            "Average fast food. Nothing terrible, nothing great.",
            "Burger was okay, but they forgot the extra sauce."
        ],
        2: [
            "Soggy fries and a dry burger patty."
        ],
        1: [
            "Order was completely wrong and the food was cold."
        ]
    },
    "DEFAULT": {
        5: [
            "Absolutely fantastic food! Everything was fresh and flavorful.",
            "Great portions, excellent quality, and fast delivery.",
            "One of my favorite places to order from. Always consistent.",
            "Highly recommended. The presentation and taste were perfect."
        ],
        4: [
            "Very good food, came warm and well-packaged.",
            "Tasty and satisfying, but just slightly overpriced.",
            "Solid meal. I will definitely order from here again."
        ],
        3: [
            "Decent food, but nothing that stands out.",
            "It was okay, but I've had better for the price."
        ],
        2: [
            "Food arrived cold and portions were quite small."
        ],
        1: [
            "Very disappointing experience. Quality was poor."
        ]
    }
}

class Command(BaseCommand):
    help = "Seeds realistic demo reviews for restaurants."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the command without saving to the database',
        )

    def get_template(self, cuisine_name, rating, rng):
        cuisine_templates = TEMPLATES.get(cuisine_name, TEMPLATES["DEFAULT"])
        if rating not in cuisine_templates:
            cuisine_templates = TEMPLATES["DEFAULT"]
        
        choices = cuisine_templates[rating]
        return rng.choice(choices)

    def handle(self, *args, **options):
        is_dry_run = options['dry_run']
        
        if is_dry_run:
            self.stdout.write(self.style.WARNING("=== DRY RUN MODE: No changes will be saved ==="))

        # Ensure demo users exist
        demo_users = []
        for i in range(1, DEMO_USER_COUNT + 1):
            email = f"{DEMO_USER_PREFIX}{i:02d}@{DEMO_USER_DOMAIN}"
            if not is_dry_run:
                user, _ = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': UKRAINIAN_NAMES[(i - 1) % len(UKRAINIAN_NAMES)],
                        'is_verified': True,
                        'role': 'CLIENT',
                        'is_staff': False,
                        'is_superuser': False
                    }
                )
                # Ensure they have a password
                if not user.has_usable_password():
                    user.set_password('DemoPass123!')
                    user.save()
                demo_users.append(user)
            else:
                demo_users.append(User(id=i, email=email))

        active_restaurants = Restaurant.objects.filter(is_active=True).select_related('cuisine')
        
        total_restaurants = 0
        total_reviews_created = 0
        total_reviews_skipped = 0
        total_synthetic_orders = 0

        # Weights: 5-star (60%), 4-star (30%), 3-star (7%), 2-star (2%), 1-star (1%)
        rating_choices = [5, 4, 3, 2, 1]
        rating_weights = [60, 30, 7, 2, 1]

        for restaurant in active_restaurants:
            total_restaurants += 1
            # Deterministic generator per restaurant
            rng = random.Random(restaurant.id)
            target = rng.randint(7, 10)

            # Count EXISTING seeded reviews for this restaurant
            seeded_reviews_count = Review.objects.filter(
                restaurant=restaurant,
                client__email__endswith=DEMO_USER_DOMAIN
            ).count()

            missing = target - seeded_reviews_count
            if missing <= 0:
                total_reviews_skipped += target
                continue

            # Need to create 'missing' reviews.
            # Pick 'missing' unique demo users
            available_users = [u for u in demo_users if not Review.objects.filter(
                restaurant=restaurant, client_id=u.id
            ).exists()]
            
            # Shuffle deterministically
            rng.shuffle(available_users)
            users_to_use = available_users[:missing]

            # Get menu items for the order
            menu_items = list(MenuItem.objects.filter(restaurant=restaurant, is_available=True)[:5])

            if not is_dry_run:
                with transaction.atomic():
                    for user in users_to_use:
                        # 1. Create Synthetic Order
                        order = Order.objects.create(
                            client=user,
                            restaurant=restaurant,
                            status=Order.STATUS_COMPLETED,
                            total_price=Decimal("0.00"),
                            street="Demo Street",
                            building="1"
                        )
                        total_synthetic_orders += 1

                        # 2. Create OrderItems
                        total_price = Decimal("0.00")
                        if menu_items:
                            # Pick 1-3 random menu items
                            num_items = rng.randint(1, min(3, len(menu_items)))
                            selected_items = rng.sample(menu_items, num_items)
                            
                            for mi in selected_items:
                                qty = rng.randint(1, 2)
                                price = mi.price
                                OrderItem.objects.create(
                                    order=order,
                                    menu_item=mi,
                                    quantity=qty,
                                    price=price,
                                    menu_item_name_snapshot=mi.name,
                                    restaurant_name_snapshot=restaurant.name
                                )
                                total_price += price * qty
                        
                        order.total_price = total_price
                        order.save(update_fields=['total_price'])

                        # 3. Create Review
                        rating = rng.choices(rating_choices, weights=rating_weights, k=1)[0]
                        cuisine_name = restaurant.cuisine.name if restaurant.cuisine else "DEFAULT"
                        comment = self.get_template(cuisine_name, rating, rng)

                        Review.objects.create(
                            client=user,
                            restaurant=restaurant,
                            order=order,
                            rating=rating,
                            comment=comment
                        )
                        total_reviews_created += 1
            else:
                total_synthetic_orders += missing
                total_reviews_created += missing
                self.stdout.write(f'[DRY RUN] Would create {missing} reviews for {restaurant.name} (target: {target}, existing seeded: {seeded_reviews_count})')

        self.stdout.write(self.style.SUCCESS(f"\nSeeding Report:"))
        self.stdout.write(f"Active restaurants processed: {total_restaurants}")
        self.stdout.write(f"Demo users processed/created: {DEMO_USER_COUNT}")
        self.stdout.write(f"Synthetic orders created: {total_synthetic_orders}")
        self.stdout.write(f"Reviews created: {total_reviews_created}")
        self.stdout.write(f"Reviews skipped (already met target): {total_reviews_skipped}")

