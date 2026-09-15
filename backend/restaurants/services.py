"""
Domain services for restaurant/menu vocabulary and search.

The MCP/AI tool layer (ai/tools/domain_tools.py) calls into these;
nothing here duplicates ORM logic that also lives elsewhere.
CandidateRetriever in ai/services.py stays the single source of truth
for menu *search* filtering (search_menu tool wraps it directly), so
there is exactly one query implementation to later upgrade to
semantic retrieval.
"""

from django.db.models import Count, Q

from .models import Category, Cuisine, MenuTag, Restaurant


class MenuVocabularyService:
    """Exposes the vocabulary that actually exists in BiteUp's catalog,
    instead of the AI having to guess or rely on prompt-hardcoded lists.
    """

    @staticmethod
    def get_tags(in_use_only=True):
        qs = MenuTag.objects.all()
        if in_use_only:
            qs = qs.annotate(
                usage_count=Count(
                    "menu_items", filter=Q(menu_items__is_available=True)
                )
            ).filter(usage_count__gt=0)
        else:
            qs = qs.annotate(usage_count=Count("menu_items"))
        return [
            {"name": tag.name, "slug": tag.slug, "usage_count": tag.usage_count}
            for tag in qs.order_by("name")
        ]

    @staticmethod
    def get_cuisines(in_use_only=True):
        qs = Cuisine.objects.all()
        if in_use_only:
            qs = qs.annotate(usage_count=Count("restaurants")).filter(
                usage_count__gt=0
            )
        else:
            qs = qs.annotate(usage_count=Count("restaurants"))
        return [
            {"name": cuisine.name, "usage_count": cuisine.usage_count}
            for cuisine in qs.order_by("name")
        ]

    @staticmethod
    def get_categories(in_use_only=True):
        qs = Category.objects.all()
        if in_use_only:
            qs = qs.annotate(
                usage_count=Count(
                    "menu_items", filter=Q(menu_items__is_available=True)
                )
            ).filter(usage_count__gt=0)
        else:
            qs = qs.annotate(usage_count=Count("menu_items"))
        return [
            {"name": category.name, "usage_count": category.usage_count}
            for category in qs.order_by("name")
        ]


class RestaurantSearchService:
    @staticmethod
    def search(query=None, cuisine=None, min_rating=None, is_open_now=None, limit=20):
        qs = Restaurant.objects.select_related("cuisine").prefetch_related(
            "opening_hours"
        )

        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if cuisine:
            qs = qs.filter(cuisine__name__iexact=cuisine)
        if min_rating is not None:
            qs = qs.filter(rating__gte=min_rating)

        qs = qs.order_by("-rating", "-review_count")[: max(1, min(limit, 50))]

        results = list(qs)
        if is_open_now is not None:
            # is_open_now is a Python property (depends on wall-clock time),
            # not a DB column, so this filter runs in-memory over the
            # already-limited page rather than in SQL.
            results = [r for r in results if r.is_open_now == is_open_now]

        return [RestaurantSearchService._serialize(r) for r in results]

    @staticmethod
    def get(restaurant_id):
        try:
            restaurant = (
                Restaurant.objects.select_related("cuisine")
                .prefetch_related("opening_hours")
                .get(pk=restaurant_id)
            )
        except Restaurant.DoesNotExist:
            return None
        return RestaurantSearchService._serialize(restaurant, detailed=True)

    @staticmethod
    def _serialize(restaurant, detailed=False):
        data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "cuisine": restaurant.cuisine.name,
            "rating": float(restaurant.rating) if restaurant.rating is not None else None,
            "review_count": restaurant.review_count,
            "delivery_time": restaurant.delivery_time,
            "is_open_now": restaurant.is_open_now,
        }
        if detailed:
            data.update(
                {
                    "description": restaurant.description,
                    "address": restaurant.address,
                    "image_url": restaurant.resolved_image_url,
                }
            )
        return data