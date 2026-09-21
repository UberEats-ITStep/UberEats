from dataclasses import dataclass
from decimal import Decimal

from django.contrib.auth import get_user_model

from orders.models import Order, OrderItem
from restaurants.models import Category, Cuisine, MenuItem, MenuTag, Restaurant


ITEM_DEFINITIONS = (
    ("margherita", "Italian", "Italian Kitchen", "Pizza", "Margherita Pizza", "Comforting vegetarian pizza", "245.00", True, False, ("pizza", "comforting", "cozy")),
    ("vegetarian_pizza", "Italian", "Italian Kitchen", "Pizza", "Garden Pizza", "Fresh vegetarian pizza", "280.00", True, False, ("pizza", "vegetarian", "filling")),
    ("cheese_pasta", "Italian", "Italian Kitchen", "Pasta", "Four Cheese Pasta", "Creamy indulgent pasta", "265.00", True, False, ("comforting", "indulgent", "cozy")),
    ("beef_burger", "American", "Burger House", "Burgers", "Double Beef Burger", "Rich beef burger", "290.00", False, False, ("beef", "greasy", "indulgent")),
    ("fries", "American", "Burger House", "Sides", "Loaded Fries", "Crispy greasy fries", "95.00", True, False, ("greasy", "indulgent")),
    ("fire_chicken", "American", "Burger House", "Mains", "Fire Chicken", "Spicy grilled chicken", "230.00", False, False, ("chicken", "spicy")),
    ("ramen", "Japanese", "Tokyo Bowl", "Ramen", "Miso Ramen", "Warm comforting ramen", "220.00", False, False, ("comforting", "cozy", "filling")),
    ("sushi_set", "Japanese", "Tokyo Bowl", "Sushi", "Chef Sushi Set", "A varied sushi set", "320.00", False, False, ("sushi", "interesting")),
    ("vegan_roll", "Japanese", "Tokyo Bowl", "Sushi", "Avocado Vegan Roll", "Fresh vegan roll", "180.00", True, True, ("vegan", "fresh", "healthy")),
    ("vegan_bowl", "Healthy", "Green Table", "Bowls", "Protein Vegan Bowl", "Light but filling vegan bowl", "210.00", True, True, ("vegan", "light", "filling", "healthy")),
    ("garden_salad", "Healthy", "Green Table", "Salads", "Garden Salad", "Fresh healthy salad", "150.00", True, True, ("fresh", "healthy", "light")),
    ("chicken_salad", "Healthy", "Green Table", "Salads", "Chicken Power Salad", "Light filling chicken salad", "225.00", False, False, ("chicken", "light", "filling")),
)


@dataclass
class EvaluationFixture:
    items: dict[str, MenuItem]
    users: dict[str, object]


class EvaluationFixtureFactory:
    prefix = "AI Evaluation"

    def create(self) -> EvaluationFixture:
        items = self._create_catalog()
        users = self._create_users(items)
        return EvaluationFixture(items=items, users=users)

    def _create_catalog(self) -> dict[str, MenuItem]:
        cuisines = {}
        categories = {}
        restaurants = {}
        items = {}

        for definition in ITEM_DEFINITIONS:
            (
                item_key,
                cuisine_name,
                restaurant_name,
                category_name,
                name,
                description,
                price,
                is_vegetarian,
                is_vegan,
                tags,
            ) = definition
            cuisine = cuisines.get(cuisine_name)
            if cuisine is None:
                cuisine = Cuisine.objects.create(
                    name=f"{self.prefix} {cuisine_name}"
                )
                cuisines[cuisine_name] = cuisine
            category = categories.get(category_name)
            if category is None:
                category = Category.objects.create(
                    name=f"{self.prefix} {category_name}"
                )
                categories[category_name] = category
            restaurant = restaurants.get(restaurant_name)
            if restaurant is None:
                restaurant = Restaurant.objects.create(
                    catalog_key=f"ai-evaluation-{restaurant_name.lower().replace(' ', '-')}",
                    name=f"{self.prefix} {restaurant_name}",
                    cuisine=cuisine,
                    rating=Decimal("4.50"),
                    is_active=True,
                )
                restaurants[restaurant_name] = restaurant
            item = MenuItem.objects.create(
                restaurant=restaurant,
                category=category,
                name=name,
                description=description,
                price=Decimal(price),
                is_available=True,
                is_vegetarian=is_vegetarian,
                is_vegan=is_vegan,
            )
            item.tags.set([
                MenuTag.objects.get_or_create(name=f"{self.prefix} {tag}")[0]
                for tag in tags
            ])
            items[item_key] = item
        return items

    def _create_users(self, items: dict[str, MenuItem]) -> dict[str, object]:
        user_model = get_user_model()
        users = {
            key: user_model.objects.create_user(
                username=f"ai-eval-{key}",
                email=f"ai-eval-{key}@example.test",
                password="EvaluationOnly123!",
                is_verified=True,
            )
            for key in ("cold_start", "italian_burger", "japanese", "vegetarian")
        }
        histories = {
            "italian_burger": ("margherita", "cheese_pasta", "beef_burger"),
            "japanese": ("ramen", "sushi_set", "vegan_roll"),
            "vegetarian": ("vegan_bowl", "vegetarian_pizza", "garden_salad"),
        }
        for profile, item_keys in histories.items():
            for item_key in item_keys:
                item = items[item_key]
                order = Order.objects.create(
                    client=users[profile],
                    restaurant=item.restaurant,
                    status=Order.STATUS_COMPLETED,
                    total_price=item.price,
                    street="Evaluation Street",
                    building="1",
                    restaurant_name_snapshot=item.restaurant.name,
                )
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    quantity=1,
                    price=item.price,
                    menu_item_name_snapshot=item.name,
                    restaurant_name_snapshot=item.restaurant.name,
                )
        return users