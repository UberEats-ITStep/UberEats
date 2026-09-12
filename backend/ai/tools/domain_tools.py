"""
BiteUp domain tools.

Each tool is a thin, validated wrapper around an existing Django
domain service (restaurants/services.py, orders/services.py) or, for
search_menu, the existing CandidateRetriever. No ORM/business logic
is duplicated here.

    MCP Tool -> BiteUp Domain Service -> Django ORM -> PostgreSQL

search_menu is deliberately "dumb" (literal keyword matching via
CandidateRetriever) today. The AI Semantic Retrieval ticket can
replace CandidateRetriever's internals without this tool's name,
input schema, or output shape changing at all.
"""

from restaurants.models import MenuItem
from restaurants.services import MenuVocabularyService, RestaurantSearchService

from . import schemas
from .base import BaseTool


class GetAvailableTagsTool(BaseTool):
    name = "get_available_tags"
    description = "List the menu tags that actually exist in BiteUp's catalog."
    input_serializer_class = schemas.GetAvailableTagsSerializer

    def run(self, validated_args, context):
        tags = MenuVocabularyService.get_tags(in_use_only=validated_args["in_use_only"])
        return {"tags": tags}


class GetAvailableCuisinesTool(BaseTool):
    name = "get_available_cuisines"
    description = "List the cuisines that actually exist in BiteUp's catalog."
    input_serializer_class = schemas.GetAvailableCuisinesSerializer

    def run(self, validated_args, context):
        cuisines = MenuVocabularyService.get_cuisines(
            in_use_only=validated_args["in_use_only"]
        )
        return {"cuisines": cuisines}


class GetAvailableCategoriesTool(BaseTool):
    name = "get_available_categories"
    description = "List the menu categories that actually exist in BiteUp's catalog."
    input_serializer_class = schemas.GetAvailableCategoriesSerializer

    def run(self, validated_args, context):
        categories = MenuVocabularyService.get_categories(
            in_use_only=validated_args["in_use_only"]
        )
        return {"categories": categories}


class SearchMenuTool(BaseTool):
    name = "search_menu"
    description = "Search BiteUp's menu items using structured filters."
    input_serializer_class = schemas.SearchMenuSerializer

    def run(self, validated_args, context):
        # Local import avoids a circular import between ai.services and
        # ai.tools at module load time (ai.services also imports the
        # tool registry to fetch vocabulary).
        from ai.services import CandidateRetriever

        intent = {
            "max_price": validated_args["max_price"],
            "is_vegetarian": validated_args["is_vegetarian"],
            "is_vegan": validated_args["is_vegan"],
            "keywords": [validated_args["query"]] if validated_args["query"] else [],
            "categories": [validated_args["category"]] if validated_args["category"] else [],
            "cuisines": [validated_args["cuisine"]] if validated_args["cuisine"] else [],
        }

        candidates = CandidateRetriever().retrieve(intent)
        limit = validated_args["limit"]

        items = [
            {
                "id": c["id"],
                "name": c["name"],
                "restaurant": c["restaurant_name"],
                "price": c["price"],
                "tags": c["tags"],
                "is_vegetarian": c["is_vegetarian"],
                "is_vegan": c["is_vegan"],
            }
            for c in candidates[:limit]
        ]
        return {"items": items}


class SearchRestaurantsTool(BaseTool):
    name = "search_restaurants"
    description = "Search BiteUp's restaurants using structured filters."
    input_serializer_class = schemas.SearchRestaurantsSerializer

    def run(self, validated_args, context):
        restaurants = RestaurantSearchService.search(
            query=validated_args["query"] or None,
            cuisine=validated_args["cuisine"],
            min_rating=validated_args["min_rating"],
            is_open_now=validated_args["is_open_now"],
            limit=validated_args["limit"],
        )
        return {"restaurants": restaurants}


class GetMenuItemTool(BaseTool):
    name = "get_menu_item"
    description = "Fetch a single menu item by id."
    input_serializer_class = schemas.GetMenuItemSerializer

    def run(self, validated_args, context):
        try:
            item = (
                MenuItem.objects.select_related("restaurant", "category")
                .prefetch_related("tags")
                .get(pk=validated_args["menu_item_id"])
            )
        except MenuItem.DoesNotExist:
            return {"item": None}

        return {
            "item": {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "restaurant": item.restaurant.name,
                "category": item.category.name,
                "tags": [t.name for t in item.tags.all()],
                "is_vegetarian": item.is_vegetarian,
                "is_vegan": item.is_vegan,
                "is_available": item.is_available,
                "calories": item.calories,
            }
        }


class GetRestaurantTool(BaseTool):
    name = "get_restaurant"
    description = "Fetch a single restaurant by id."
    input_serializer_class = schemas.GetRestaurantSerializer

    def run(self, validated_args, context):
        restaurant = RestaurantSearchService.get(validated_args["restaurant_id"])
        return {"restaurant": restaurant}


class GetUserOrderHistoryTool(BaseTool):
    """
    Reference implementation for future user-specific tools (see ticket
    goal 6). The user is taken exclusively from `context.user`; the
    input schema has no user id field at all, so there is no argument
    a model could use to request another user's history. Not wired
    into the recommendation pipeline yet - included so the isolation
    pattern is established and tested before it's needed elsewhere.
    """

    name = "get_user_order_history"
    description = "Get the authenticated user's recent completed orders."
    input_serializer_class = schemas.GetUserOrderHistorySerializer
    requires_user_context = True

    def run(self, validated_args, context):
        from orders.services import OrderHistoryService

        orders = OrderHistoryService.get_recent_orders(
            user=context.user, limit=validated_args["limit"]
        )
        return {"orders": orders}


def register_domain_tools(registry):
    for tool_cls in (
        GetAvailableTagsTool,
        GetAvailableCuisinesTool,
        GetAvailableCategoriesTool,
        SearchMenuTool,
        SearchRestaurantsTool,
        GetMenuItemTool,
        GetRestaurantTool,
        GetUserOrderHistoryTool,
    ):
        registry.register(tool_cls())
    return registry