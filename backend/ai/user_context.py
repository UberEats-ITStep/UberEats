from collections import Counter
from decimal import Decimal

from orders.models import Order
from favorites.models import Favorite
from reviews.models import Review
from users.models import UserEvent


class UserContextBuilder:
    MAX_ORDERS = 50
    MAX_TOP_ITEMS = 5
    MAX_TOP_RESTAURANTS = 5
    MAX_TOP_CUISINES = 5
    MAX_TOP_CATEGORIES = 5
    MAX_RECENT_ORDERS = 5

    def build(self, user):
        orders = list(
            Order.objects
            .filter(
                client=user,
                status=Order.STATUS_COMPLETED,
            )
            .select_related(
                "restaurant",
                "restaurant__cuisine",
            )
            .prefetch_related(
                "items__menu_item__category",
                "items__menu_item__restaurant__cuisine",
            )
            .order_by("-created_at")[:self.MAX_ORDERS]
        )

        review_count = Review.objects.filter(client=user).count()
        favorite_restaurants = self._get_favorite_restaurants(user)
        highly_rated_restaurants = self._get_highly_rated_restaurants(user)

        if not orders:
            context = self._empty_context(user)
            context["review_count"] = review_count
            context["favorite_restaurants"] = favorite_restaurants
            context["highly_rated_restaurants"] = highly_rated_restaurants
            context["has_history"] = bool(
                review_count
                or favorite_restaurants
                or highly_rated_restaurants
            )
            return context

        item_counter = Counter()
        restaurant_counter = Counter()
        cuisine_counter = Counter()
        category_counter = Counter()

        vegetarian_count = 0
        vegan_count = 0
        purchased_item_count = 0

        order_values = []
        recent_orders = []

        for order in orders:
            order_total = Decimal(order.total_price or 0)
            order_values.append(order_total)

            restaurant_name = (
                order.restaurant_name_snapshot
                or order.restaurant.name
            )

            restaurant_counter[restaurant_name] += 1

            recent_order_items = []

            for order_item in order.items.all():
                quantity = order_item.quantity or 0

                item_name = (
                    order_item.menu_item_name_snapshot
                    or order_item.menu_item.name
                )

                item_counter[item_name] += quantity
                purchased_item_count += quantity

                menu_item = order_item.menu_item

                if menu_item.category:
                    category_counter[menu_item.category.name] += quantity

                if menu_item.restaurant.cuisine:
                    cuisine_counter[
                        menu_item.restaurant.cuisine.name
                    ] += quantity

                if menu_item.is_vegetarian:
                    vegetarian_count += quantity

                if menu_item.is_vegan:
                    vegan_count += quantity

                recent_order_items.append({
                    "menu_item": item_name,
                    "restaurant": (
                        order_item.restaurant_name_snapshot
                        or order.restaurant_name_snapshot
                        or order.restaurant.name
                    ),
                    "quantity": quantity,
                    "price": float(order_item.price),
                })

            if len(recent_orders) < self.MAX_RECENT_ORDERS:
                recent_orders.append({
                    "restaurant": restaurant_name,
                    "total": float(order_total),
                    "created_at": order.created_at.isoformat(),
                    "items": recent_order_items[:10],
                })


        average_order_value = (
            sum(order_values, Decimal("0")) / len(order_values)
        )
        
        # Determine consumed_item_ids from the order history
        consumed_item_ids = {item.menu_item_id for order in orders for item in order.items.all() if item.menu_item_id}

        return {
            "has_history": True,
            "completed_order_count": len(orders),
            "review_count": review_count,
            "top_cuisines": self._top_counter(
                cuisine_counter,
                self.MAX_TOP_CUISINES,
            ),
            "top_categories": self._top_counter(
                category_counter,
                self.MAX_TOP_CATEGORIES,
            ),
            "top_restaurants": self._top_counter(
                restaurant_counter,
                self.MAX_TOP_RESTAURANTS,
            ),
            "top_menu_items": self._top_counter(
                item_counter,
                self.MAX_TOP_ITEMS,
            ),
            "favorite_restaurants": favorite_restaurants,
            "highly_rated_restaurants": highly_rated_restaurants,
            "average_order_value": round(
                float(average_order_value),
                2,
            ),
            "dietary_preferences": self._build_dietary_preferences(
                vegetarian_count,
                vegan_count,
                purchased_item_count,
            ),
            "recent_orders": recent_orders,
            "recent_events": self._get_recent_events(user),
            "consumed_item_ids": list(consumed_item_ids),
        }




    def _get_recent_events(self, user):
        # Fetch the most recent 100 events
        events = list(UserEvent.objects.filter(user=user).order_by("-created_at")[:100])
        recent_searches = []
        recent_ai_searches = []
        recent_viewed_items = set()
        recent_viewed_restaurants = set()
        recent_cart_adds = set()
        recent_cart_removes = set()

        for event in events:
            evt_type = event.event_type
            meta = event.metadata
            
            if evt_type == UserEvent.EventType.SEARCH:
                q = meta.get("query")
                if q and q not in recent_searches:
                    recent_searches.append(q)
            elif evt_type == UserEvent.EventType.AI_SEARCH:
                q = meta.get("query")
                if q and q not in recent_ai_searches:
                    recent_ai_searches.append(q)
            elif evt_type == UserEvent.EventType.MENU_ITEM_VIEW:
                item_id = meta.get("menu_item_id")
                if item_id: recent_viewed_items.add(item_id)
            elif evt_type == UserEvent.EventType.RESTAURANT_VIEW:
                rest_id = meta.get("restaurant_id")
                if rest_id: recent_viewed_restaurants.add(rest_id)
            elif evt_type == UserEvent.EventType.ADD_TO_CART:
                item_id = meta.get("menu_item_id")
                if item_id: recent_cart_adds.add(item_id)
            elif evt_type == UserEvent.EventType.REMOVE_FROM_CART:
                item_id = meta.get("menu_item_id")
                if item_id: recent_cart_removes.add(item_id)

        return {
            "searches": recent_searches[:5],
            "ai_searches": recent_ai_searches[:5],
            "viewed_item_ids": list(recent_viewed_items),
            "viewed_restaurant_ids": list(recent_viewed_restaurants),
            "cart_add_item_ids": list(recent_cart_adds),
            "cart_remove_item_ids": list(recent_cart_removes)
        }

    def _empty_context(self, user):
        return {
            "has_history": False,
            "completed_order_count": 0,
            "review_count": 0,
            "top_cuisines": [],
            "top_categories": [],
            "top_restaurants": [],
            "top_menu_items": [],
            "favorite_restaurants": [],
            "highly_rated_restaurants": [],
            "average_order_value": None,
            "typical_price_range": [None, None],
            "dietary_preferences": {
                "vegetarian_ratio": 0,
                "vegan_ratio": 0,
                "vegetarian_tendency": False,
                "vegan_tendency": False,
            },
            "recent_orders": [],
            "recent_events": self._get_recent_events(user),
            "consumed_item_ids": [],
        }

    @staticmethod
    def _top_counter(counter, limit):
        return [
            {
                "name": name,
                "count": count,
            }
            for name, count in counter.most_common(limit)
        ]

    @staticmethod
    def _calculate_price_range(order_values):
        if not order_values:
            return [None, None]

        values = [float(value) for value in order_values]

        return [
            round(min(values), 2),
            round(max(values), 2),
        ]

    @staticmethod
    def _build_dietary_preferences(
        vegetarian_count,
        vegan_count,
        purchased_item_count,
    ):
        if purchased_item_count <= 0:
            return {
                "vegetarian_ratio": 0,
                "vegan_ratio": 0,
                "vegetarian_tendency": False,
                "vegan_tendency": False,
            }

        vegetarian_ratio = (
            vegetarian_count / purchased_item_count
        )

        vegan_ratio = (
            vegan_count / purchased_item_count
        )

        return {
            "vegetarian_ratio": round(vegetarian_ratio, 2),
            "vegan_ratio": round(vegan_ratio, 2),
            "vegetarian_tendency": vegetarian_ratio >= 0.60,
            "vegan_tendency": vegan_ratio >= 0.60,
        }

    def _get_favorite_restaurants(self, user):
        favorites = (
            Favorite.objects
            .filter(user=user)
            .select_related("restaurant")
            .order_by("-created_at")[:self.MAX_TOP_RESTAURANTS]
        )

        return [
            {
                "id": favorite.restaurant.id,
                "name": favorite.restaurant.name,
            }
            for favorite in favorites
            if favorite.restaurant is not None
        ]

    def _get_highly_rated_restaurants(self, user):
        reviews = (
            Review.objects
            .filter(
                client=user,
                rating__gte=4,
            )
            .select_related("restaurant")
            .order_by("-id")[:self.MAX_TOP_RESTAURANTS]
        )

        result = []
        seen_restaurants = set()

        for review in reviews:
            restaurant = review.restaurant

            if restaurant is None:
                continue

            if restaurant.id in seen_restaurants:
                continue

            seen_restaurants.add(restaurant.id)

            result.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "rating": float(review.rating),
            })

            if len(result) >= self.MAX_TOP_RESTAURANTS:
                break

        return result
