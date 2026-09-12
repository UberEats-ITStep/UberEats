import os
from decimal import Decimal
from unittest.mock import patch
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from restaurants.models import (
    Restaurant,
    Cuisine,
    Category,
    MenuItem,
    MenuTag,
)

from ai.services import (
    GroqAPIException,
    IntentExtractor,
    RecommendationOrchestrator,
    VocabularyProvider,
)

from ai.user_context import UserContextBuilder

from ai.tools import registry
from ai.tools.context import ToolContext
from ai.tools.errors import (
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolUnauthorizedError,
    ToolValidationError,
)

from favorites.models import Favorite
from orders.models import Order, OrderItem
from reviews.models import Review


User = get_user_model()


class AIRecommendTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="pwd",
            role="CLIENT",
            is_verified=True,
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@test.com",
            password="pwd",
            role="CLIENT",
            is_verified=True,
        )

        self.throttle_patcher = patch(
            "rest_framework.throttling.ScopedRateThrottle.allow_request",
            return_value=True,
        )
        self.throttle_patcher.start()
        self.addCleanup(self.throttle_patcher.stop)

        self.url = reverse("ai:recommend")

        self.cuisine = Cuisine.objects.create(
            name="Japanese"
        )

        self.italian_cuisine = Cuisine.objects.create(
            name="Italian"
        )

        self.restaurant = Restaurant.objects.create(
            name="Sushi Place",
            cuisine=self.cuisine,
        )

        self.italian_restaurant = Restaurant.objects.create(
            name="Italian Place",
            cuisine=self.italian_cuisine,
        )

        self.category = Category.objects.create(
            name="Sushi"
        )

        self.pasta_category = Category.objects.create(
            name="Pasta"
        )

        self.tag_spicy = MenuTag.objects.create(
            name="spicy"
        )

        self.item1 = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Spicy Tuna Roll",
            description="Very spicy",
            price=Decimal("150.00"),
            is_available=True,
            is_vegetarian=False,
            is_vegan=False,
        )

        self.item1.tags.add(self.tag_spicy)

        self.item2 = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Avocado Roll",
            description="Fresh avocado",
            price=Decimal("100.00"),
            is_available=True,
            is_vegetarian=True,
            is_vegan=True,
        )

        self.item3 = MenuItem.objects.create(
            restaurant=self.italian_restaurant,
            category=self.pasta_category,
            name="Carbonara",
            description="Classic Italian pasta",
            price=Decimal("250.00"),
            is_available=True,
            is_vegetarian=False,
            is_vegan=False,
        )

    # =============================================================
    # AUTHENTICATION
    # =============================================================

    def test_unauthenticated(self):
        response = self.client.post(
            self.url,
            {"query": "sushi"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =============================================================
    # BASIC RECOMMENDATION
    # =============================================================

    @skipUnless(
        settings.GROQ_API_KEY and os.getenv("RUN_GROQ_INTEGRATION_TESTS") == "1",
        "Set GROQ_API_KEY and RUN_GROQ_INTEGRATION_TESTS=1 to run",
    )
    def test_temporary_real_groq_recommendation(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"query": "Recommend vegetarian food under 200 UAH"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.assertIn(
            "recommendations",
            response.data,
        )

    @patch("ai.services.GroqClient.chat_completion")
    def test_successful_recommendation(self, mock_groq):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": 200,
                "is_vegetarian": True,
                "is_vegan": None,
                "keywords": [],
                "categories": ["Sushi"],
                "cuisines": ["Japanese"],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item2.id,
                        "reason": "Vegetarian and under 200.",
                    }
                ],
                "summary": "Here is your roll.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "vegetarian sushi under 200"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()

        self.assertEqual(
            data["message"],
            "Here is your roll.",
        )

        self.assertEqual(
            len(data["recommendations"]),
            1,
        )

        self.assertEqual(
            data["recommendations"][0]["menu_item"]["id"],
            self.item2.id,
        )

        self.assertEqual(
            mock_groq.call_count,
            2,
        )

    # =============================================================
    # EMPTY CANDIDATES
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_empty_candidates_skips_ranking(self, mock_groq):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": 1,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            }
        ]

        response = self.client.post(
            self.url,
            {
                "query": "cheap food"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            mock_groq.call_count,
            1,
        )

        self.assertEqual(
            response.json()["recommendations"],
            [],
        )

    # =============================================================
    # HALLUCINATION PROTECTION
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_hallucinated_id_discarded(self, mock_groq):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": 9999,
                        "reason": "Hallucinated",
                    },
                    {
                        "menu_item_id": self.item1.id,
                        "reason": "Valid",
                    },
                ],
                "summary": "Done.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "food"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()

        self.assertEqual(
            len(data["recommendations"]),
            1,
        )

        self.assertEqual(
            data["recommendations"][0]["menu_item"]["id"],
            self.item1.id,
        )

    # =============================================================
    # GROQ ERROR HANDLING
    # =============================================================

    @patch("ai.services.requests.post")
    def test_groq_timeout_handled(self, mock_post):
        import requests

        self.client.force_authenticate(
            user=self.user
        )

        mock_post.side_effect = requests.exceptions.Timeout(
            "Timeout"
        )

        response = self.client.post(
            self.url,
            {
                "query": "food"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    # =============================================================
    # USER CONTEXT - COLD START
    # =============================================================

    def test_user_without_history_gets_empty_context(self):
        context = UserContextBuilder().build(
            self.user
        )

        self.assertFalse(
            context["has_history"]
        )

        self.assertEqual(
            context["top_cuisines"],
            [],
        )

        self.assertEqual(
            context["top_categories"],
            [],
        )

        self.assertEqual(
            context["top_restaurants"],
            [],
        )

        self.assertEqual(
            context["top_menu_items"],
            [],
        )

        self.assertEqual(
            context["favorite_restaurants"],
            [],
        )

        self.assertEqual(
            context["highly_rated_restaurants"],
            [],
        )

        self.assertIsNone(
            context["average_order_value"]
        )

        self.assertEqual(
            context["typical_price_range"],
            [None, None],
        )

        self.assertEqual(
            context["recent_orders"],
            [],
        )

        self.assertEqual(
            context["completed_order_count"],
            0,
        )

        self.assertEqual(
            context["review_count"],
            0,
        )

    # =============================================================
    # USER CONTEXT - ISOLATION
    # =============================================================

    def test_users_have_independent_contexts(self):
        context_user_1 = UserContextBuilder().build(
            self.user
        )

        context_user_2 = UserContextBuilder().build(
            self.other_user
        )

        self.assertIsNot(
            context_user_1,
            context_user_2,
        )

        self.assertEqual(
            context_user_1["completed_order_count"],
            0,
        )

        self.assertEqual(
            context_user_2["completed_order_count"],
            0,
        )

    # =============================================================
    # USER CONTEXT - DIETARY STRUCTURE
    # =============================================================

    def test_empty_user_has_valid_dietary_context(self):
        context = UserContextBuilder().build(
            self.user
        )

        dietary = context[
            "dietary_preferences"
        ]

        self.assertIn(
            "vegetarian_ratio",
            dietary,
        )

        self.assertIn(
            "vegan_ratio",
            dietary,
        )

        self.assertGreaterEqual(
            dietary["vegetarian_ratio"],
            0,
        )

        self.assertLessEqual(
            dietary["vegetarian_ratio"],
            1,
        )

        self.assertGreaterEqual(
            dietary["vegan_ratio"],
            0,
        )

        self.assertLessEqual(
            dietary["vegan_ratio"],
            1,
        )

    # =============================================================
    # PERSONALIZATION INTEGRATION
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_user_context_is_sent_to_groq(self, mock_groq):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item1.id,
                        "reason": "Matches your preferences.",
                    }
                ],
                "summary": "Based on what you usually enjoy.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "I don't know what I want"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            mock_groq.call_count,
            2,
        )

        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        self.assertIn(
            "CURRENT USER REQUEST",
            user_content,
        )

        self.assertIn(
            "AUTHORITATIVE USER CONTEXT",
            user_content,
        )

        self.assertIn(
            "AVAILABLE CANDIDATES",
            user_content,
        )

        self.assertIn(
            "I don't know what I want",
            user_content,
        )

    # =============================================================
    # PERSONALIZED SURPRISE ME
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_personalized_surprise_me(self, mock_groq):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item1.id,
                        "reason": (
                            "A Japanese option that matches "
                            "your usual preferences."
                        ),
                    }
                ],
                "summary": (
                    "Based on what you usually enjoy, "
                    "I'd go with this."
                ),
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "Surprise me"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()

        self.assertEqual(
            len(data["recommendations"]),
            1,
        )

        self.assertEqual(
            data["recommendations"][0]["menu_item"]["id"],
            self.item1.id,
        )

        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        self.assertIn(
            "Surprise me",
            user_content,
        )

        self.assertIn(
            "AUTHORITATIVE USER CONTEXT",
            user_content,
        )

    # =============================================================
    # I DON'T KNOW WHAT I WANT
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_i_dont_know_what_i_want_uses_user_context(
        self,
        mock_groq,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item1.id,
                        "reason": (
                            "This matches your historical "
                            "Japanese preference."
                        ),
                    }
                ],
                "summary": (
                    "Based on your previous choices, "
                    "this looks like a good fit."
                ),
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "I don't know what I want"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        self.assertIn(
            "I don't know what I want",
            user_content,
        )

        self.assertIn(
            "AUTHORITATIVE USER CONTEXT",
            user_content,
        )

    # =============================================================
    # EXPLICIT REQUEST HAS PRIORITY
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_explicit_request_has_priority_over_history(
        self,
        mock_groq,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": 300,
                "is_vegetarian": None,
                "is_vegan": True,
                "keywords": [],
                "categories": ["Sushi"],
                "cuisines": ["Japanese"],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item2.id,
                        "reason": (
                            "Vegan sushi under 300 UAH."
                        ),
                    }
                ],
                "summary": (
                    "Here are vegan sushi options "
                    "under 300 UAH."
                ),
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": (
                    "I want vegan sushi under 300 UAH"
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        data = response.json()

        self.assertEqual(
            len(data["recommendations"]),
            1,
        )

        self.assertEqual(
            data["recommendations"][0]["menu_item"]["id"],
            self.item2.id,
        )

        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        self.assertIn(
            "I want vegan sushi under 300 UAH",
            user_content,
        )

        self.assertIn(
            "AUTHORITATIVE USER CONTEXT",
            user_content,
        )

    # =============================================================
    # CURRENT QUERY MUST NOT BE REPLACED
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_current_query_is_always_passed_to_ranker(
        self,
        mock_groq,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        query = "vegan sushi under 300"

        mock_groq.side_effect = [
            {
                "max_price": 300,
                "is_vegetarian": None,
                "is_vegan": True,
                "keywords": [],
                "categories": ["Sushi"],
                "cuisines": ["Japanese"],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item2.id,
                        "reason": "Matches the request.",
                    }
                ],
                "summary": "Good match.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": query
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        self.assertIn(
            query,
            user_content,
        )

        self.assertIn(
            "AUTHORITATIVE USER CONTEXT",
            user_content,
        )

    # =============================================================
    # AVAILABLE CANDIDATES MUST STILL BE PROVIDED
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_ranker_receives_candidates_and_user_context(
        self,
        mock_groq,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item1.id,
                        "reason": "Good match.",
                    }
                ],
                "summary": "Recommended.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "food"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        self.assertIn(
            "Spicy Tuna Roll",
            user_content,
        )

        self.assertIn(
            "Avocado Roll",
            user_content,
        )

        self.assertIn(
            "Carbonara",
            user_content,
        )

        self.assertIn(
            "AVAILABLE CANDIDATES",
            user_content,
        )

    # =============================================================
    # DB VALIDATION AFTER PERSONALIZED RANKING
    # =============================================================

    @patch("ai.services.GroqClient.chat_completion")
    def test_personalization_does_not_disable_db_validation(
        self,
        mock_groq,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": 999999,
                        "reason": "Fake item.",
                    },
                    {
                        "menu_item_id": self.item2.id,
                        "reason": "Real item.",
                    },
                ],
                "summary": "Recommendations.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "surprise me"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        recommendations = response.json()[
            "recommendations"
        ]

        self.assertEqual(
            len(recommendations),
            1,
        )

        self.assertEqual(
            recommendations[0]["menu_item"]["id"],
            self.item2.id,
        )

    # =============================================================
    # BEHAVIORAL PROFILE
    # =============================================================

    def test_completed_orders_build_compact_behavioral_profile(self):
        first_order = Order.objects.create(
            client=self.user,
            restaurant=self.restaurant,
            status=Order.STATUS_COMPLETED,
            total_price=Decimal("200.00"),
            street="Soborna",
            building="1",
        )

        OrderItem.objects.create(
            order=first_order,
            menu_item=self.item2,
            quantity=2,
            price=self.item2.price,
        )

        second_order = Order.objects.create(
            client=self.user,
            restaurant=self.restaurant,
            status=Order.STATUS_COMPLETED,
            total_price=Decimal("300.00"),
            street="Soborna",
            building="1",
        )

        OrderItem.objects.create(
            order=second_order,
            menu_item=self.item1,
            quantity=2,
            price=self.item1.price,
        )

        ignored_order = Order.objects.create(
            client=self.user,
            restaurant=self.italian_restaurant,
            status=Order.STATUS_CANCELLED,
            total_price=Decimal("250.00"),
            street="Soborna",
            building="1",
        )

        OrderItem.objects.create(
            order=ignored_order,
            menu_item=self.item3,
            quantity=1,
            price=self.item3.price,
        )

        context = UserContextBuilder().build(self.user)

        self.assertTrue(
            context["has_history"]
        )

        self.assertEqual(
            context["completed_order_count"],
            2,
        )

        self.assertEqual(
            context["average_order_value"],
            250.0,
        )

        self.assertEqual(
            context["typical_price_range"],
            [200.0, 300.0],
        )

        self.assertEqual(
            context["top_cuisines"][0],
            {
                "name": "Japanese",
                "count": 4,
            },
        )

        self.assertEqual(
            context["top_categories"][0],
            {
                "name": "Sushi",
                "count": 4,
            },
        )

        self.assertEqual(
            context["dietary_preferences"]["vegetarian_ratio"],
            0.5,
        )

        self.assertNotIn(
            "Italian",
            {
                entry["name"]
                for entry in context["top_cuisines"]
            },
        )

        self.assertEqual(
            UserContextBuilder().build(
                self.other_user
            )["top_cuisines"],
            [],
        )

    def test_favorites_are_context_even_without_completed_orders(self):
        Favorite.objects.create(
            user=self.user,
            restaurant=self.restaurant,
        )

        context = UserContextBuilder().build(
            self.user
        )

        self.assertTrue(
            context["has_history"]
        )

        self.assertEqual(
            context["completed_order_count"],
            0,
        )

        self.assertEqual(
            context["favorite_restaurants"],
            [
                {
                    "id": self.restaurant.id,
                    "name": self.restaurant.name,
                }
            ],
        )

        self.assertEqual(
            UserContextBuilder().build(
                self.other_user
            )["favorite_restaurants"],
            [],
        )

    def test_high_rating_is_context_even_without_completed_orders(self):
        order = Order.objects.create(
            client=self.user,
            restaurant=self.restaurant,
            status=Order.STATUS_CANCELLED,
            total_price=Decimal("150.00"),
            street="Soborna",
            building="1",
        )

        Review.objects.create(
            client=self.user,
            restaurant=self.restaurant,
            order=order,
            rating=5,
        )

        context = UserContextBuilder().build(
            self.user
        )

        self.assertTrue(
            context["has_history"]
        )

        self.assertEqual(
            context["review_count"],
            1,
        )

        self.assertEqual(
            context["highly_rated_restaurants"],
            [
                {
                    "id": self.restaurant.id,
                    "name": self.restaurant.name,
                    "rating": 5.0,
                }
            ],
        )

    @patch("ai.services.GroqClient.chat_completion")
    def test_existing_item_outside_filtered_candidates_is_discarded(
        self,
        mock_groq,
    ):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            {
                "max_price": 300,
                "is_vegetarian": None,
                "is_vegan": True,
                "keywords": [],
                "categories": ["Sushi"],
                "cuisines": ["Japanese"],
            },
            {
                "recommendations": [
                    {
                        "menu_item_id": self.item3.id,
                        "reason": (
                            "Existing, but violates the request."
                        ),
                    }
                ],
                "summary": "Invalid selection.",
            },
        ]

        response = self.client.post(
            self.url,
            {
                "query": "I want vegan sushi under 300 UAH",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.json()["recommendations"],
            [],
        )


# =============================================================
# MCP TOOL REGISTRY
# =============================================================


class ToolRegistryTests(TestCase):
    def test_all_required_tools_are_registered(self):
        expected_tools = {
            "get_available_tags",
            "get_available_cuisines",
            "get_available_categories",
            "search_menu",
            "search_restaurants",
            "get_menu_item",
            "get_restaurant",
            "get_user_order_history",
        }

        # list_tools() returns discovery schema dicts (name, description,
        # input_schema, requires_user_context) - pull out the names.
        registered_tools = {
            schema["name"]
            for schema in registry.list_tools()
        }

        self.assertTrue(
            expected_tools.issubset(registered_tools),
            (
                "Missing tools: "
                f"{expected_tools - registered_tools}"
            ),
        )

    def test_tool_schema_reports_input_fields(self):
        schema = next(
            s for s in registry.list_tools() if s["name"] == "search_menu"
        )

        self.assertIn("query", schema["input_schema"])
        self.assertIn("max_price", schema["input_schema"])

    def test_unknown_tool_raises_tool_not_found_error(self):
        with self.assertRaises(ToolNotFoundError):
            registry.call(
                "unknown_tool",
                {},
            )


# =============================================================
# MCP TOOL CONTEXT
# =============================================================


class ToolContextTests(TestCase):
    def test_context_contains_user_and_request_id(self):
        user = User.objects.create_user(
            username="context_user",
            email="context@test.com",
            password="password123",
        )

        context = ToolContext(
            user=user,
            request_id="request-123",
        )

        self.assertIs(
            context.user,
            user,
        )

        self.assertEqual(
            context.request_id,
            "request-123",
        )

    def test_context_can_be_created_without_user(self):
        context = ToolContext(
            user=None,
            request_id="anonymous-request",
        )

        self.assertIsNone(
            context.user,
        )

        self.assertEqual(
            context.request_id,
            "anonymous-request",
        )


# =============================================================
# MCP DOMAIN TOOLS BASE
# =============================================================


class DomainToolsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tooluser",
            email="tool@test.com",
            password="password123",
        )

        self.cuisine = Cuisine.objects.create(
            name="Japanese",
        )

        self.other_cuisine = Cuisine.objects.create(
            name="Italian",
        )

        self.category = Category.objects.create(
            name="Sushi",
        )

        self.other_category = Category.objects.create(
            name="Pasta",
        )

        self.tag_spicy = MenuTag.objects.create(
            name="spicy",
        )

        self.tag_vegan = MenuTag.objects.create(
            name="vegan",
        )

        self.restaurant = Restaurant.objects.create(
            name="Sushi Place",
            cuisine=self.cuisine,
        )

        self.other_restaurant = Restaurant.objects.create(
            name="Italian Place",
            cuisine=self.other_cuisine,
        )

        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Spicy Tuna Roll",
            description="Spicy Japanese sushi",
            price=Decimal("150.00"),
            is_available=True,
            is_vegetarian=False,
            is_vegan=False,
        )

        self.menu_item.tags.add(
            self.tag_spicy
        )

        self.vegan_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Avocado Roll",
            description="Fresh vegan avocado sushi",
            price=Decimal("100.00"),
            is_available=True,
            is_vegetarian=True,
            is_vegan=True,
        )

        self.vegan_item.tags.add(
            self.tag_vegan
        )

        self.other_item = MenuItem.objects.create(
            restaurant=self.other_restaurant,
            category=self.other_category,
            name="Carbonara",
            description="Classic Italian pasta",
            price=Decimal("250.00"),
            is_available=True,
            is_vegetarian=False,
            is_vegan=False,
        )

        self.context = ToolContext(
            user=self.user,
            request_id="test-request",
        )


# =============================================================
# VOCABULARY TOOLS
# =============================================================


class VocabularyToolsTests(DomainToolsTestCase):
    def test_get_available_tags_returns_database_values(self):
        result = registry.call(
            "get_available_tags",
            {},
            context=self.context,
        )

        tag_names = {
            tag["name"]
            for tag in result["data"]["tags"]
        }

        self.assertIn(
            "spicy",
            tag_names,
        )

        self.assertIn(
            "vegan",
            tag_names,
        )

    def test_get_available_tags_in_use_only_excludes_unused_tags(self):
        MenuTag.objects.create(name="unused-tag")

        result = registry.call(
            "get_available_tags",
            {"in_use_only": True},
            context=self.context,
        )

        tag_names = {tag["name"] for tag in result["data"]["tags"]}
        self.assertNotIn("unused-tag", tag_names)

        result_all = registry.call(
            "get_available_tags",
            {"in_use_only": False},
            context=self.context,
        )

        tag_names_all = {tag["name"] for tag in result_all["data"]["tags"]}
        self.assertIn("unused-tag", tag_names_all)

    def test_get_available_cuisines_returns_database_values(self):
        result = registry.call(
            "get_available_cuisines",
            {},
            context=self.context,
        )

        cuisine_names = {
            cuisine["name"]
            for cuisine in result["data"]["cuisines"]
        }

        self.assertIn(
            "Japanese",
            cuisine_names,
        )

        self.assertIn(
            "Italian",
            cuisine_names,
        )

    def test_get_available_categories_returns_database_values(self):
        result = registry.call(
            "get_available_categories",
            {},
            context=self.context,
        )

        category_names = {
            category["name"]
            for category in result["data"]["categories"]
        }

        self.assertIn(
            "Sushi",
            category_names,
        )

        self.assertIn(
            "Pasta",
            category_names,
        )

    def test_vocabulary_results_are_sorted(self):
        result = registry.call(
            "get_available_cuisines",
            {},
            context=self.context,
        )

        names = [
            cuisine["name"]
            for cuisine in result["data"]["cuisines"]
        ]

        self.assertEqual(
            names,
            sorted(names, key=str.lower),
        )


# =============================================================
# MENU SEARCH TOOLS
# =============================================================


class MenuSearchToolsTests(DomainToolsTestCase):
    def test_search_menu_returns_matching_items(self):
        result = registry.call(
            "search_menu",
            {
                "query": "sushi",
            },
            context=self.context,
        )

        items = result["data"]["items"]

        self.assertIsInstance(
            items,
            list,
        )

        returned_ids = {
            item["id"]
            for item in items
        }

        self.assertIn(
            self.menu_item.id,
            returned_ids,
        )

        self.assertIn(
            self.vegan_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.other_item.id,
            returned_ids,
        )

    def test_search_menu_can_filter_by_max_price(self):
        result = registry.call(
            "search_menu",
            {
                "max_price": 120,
            },
            context=self.context,
        )

        returned_ids = {
            item["id"]
            for item in result["data"]["items"]
        }

        self.assertIn(
            self.vegan_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.menu_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.other_item.id,
            returned_ids,
        )

    def test_search_menu_can_filter_by_vegetarian(self):
        result = registry.call(
            "search_menu",
            {
                "is_vegetarian": True,
            },
            context=self.context,
        )

        returned_ids = {
            item["id"]
            for item in result["data"]["items"]
        }

        self.assertIn(
            self.vegan_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.menu_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.other_item.id,
            returned_ids,
        )

    def test_search_menu_can_filter_by_vegan(self):
        result = registry.call(
            "search_menu",
            {
                "is_vegan": True,
            },
            context=self.context,
        )

        returned_ids = {
            item["id"]
            for item in result["data"]["items"]
        }

        self.assertIn(
            self.vegan_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.menu_item.id,
            returned_ids,
        )

        self.assertNotIn(
            self.other_item.id,
            returned_ids,
        )

    def test_search_menu_returns_only_available_items(self):
        self.menu_item.is_available = False
        self.menu_item.save(
            update_fields=["is_available"],
        )

        result = registry.call(
            "search_menu",
            {
                "query": "sushi",
            },
            context=self.context,
        )

        returned_ids = {
            item["id"]
            for item in result["data"]["items"]
        }

        self.assertNotIn(
            self.menu_item.id,
            returned_ids,
        )

        self.assertIn(
            self.vegan_item.id,
            returned_ids,
        )


# =============================================================
# ENTITY TOOLS
# =============================================================


class EntityToolsTests(DomainToolsTestCase):
    def test_get_menu_item_returns_existing_item(self):
        result = registry.call(
            "get_menu_item",
            {
                "menu_item_id": self.menu_item.id,
            },
            context=self.context,
        )

        item = result["data"]["item"]

        self.assertEqual(
            item["id"],
            self.menu_item.id,
        )

        self.assertEqual(
            item["name"],
            self.menu_item.name,
        )

    def test_get_menu_item_returns_none_for_missing_item(self):
        result = registry.call(
            "get_menu_item",
            {
                "menu_item_id": 999999,
            },
            context=self.context,
        )

        self.assertIsNone(
            result["data"]["item"],
        )

    def test_get_restaurant_returns_existing_restaurant(self):
        result = registry.call(
            "get_restaurant",
            {
                "restaurant_id": self.restaurant.id,
            },
            context=self.context,
        )

        restaurant = result["data"]["restaurant"]

        self.assertEqual(
            restaurant["id"],
            self.restaurant.id,
        )

        self.assertEqual(
            restaurant["name"],
            self.restaurant.name,
        )

    def test_get_restaurant_returns_none_for_missing_restaurant(self):
        result = registry.call(
            "get_restaurant",
            {
                "restaurant_id": 999999,
            },
            context=self.context,
        )

        self.assertIsNone(
            result["data"]["restaurant"],
        )


# =============================================================
# TOOL VALIDATION
# =============================================================


class ToolValidationTests(DomainToolsTestCase):
    def test_tool_rejects_unknown_arguments(self):
        with self.assertRaises(ToolValidationError):
            registry.call(
                "get_user_order_history",
                {"user_id": self.user.id},
                context=self.context,
            )

    def test_tool_rejects_invalid_argument_type(self):
        with self.assertRaises(ToolValidationError):
            registry.call(
                "get_menu_item",
                {
                    "menu_item_id": "not-an-integer",
                },
                context=self.context,
            )

    def test_tool_rejects_missing_required_argument(self):
        with self.assertRaises(ToolValidationError):
            registry.call(
                "get_menu_item",
                {},
                context=self.context,
            )


# =============================================================
# TOOL AUTHORIZATION
# =============================================================


class ToolAuthorizationTests(DomainToolsTestCase):
    def test_order_history_requires_authenticated_user(self):
        anonymous_context = ToolContext(
            user=None,
            request_id="anonymous-request",
        )

        with self.assertRaises(ToolUnauthorizedError):
            registry.call(
                "get_user_order_history",
                {},
                context=anonymous_context,
            )

    def test_order_history_rejects_django_anonymous_user(self):
        from django.contrib.auth.models import AnonymousUser

        with self.assertRaises(ToolUnauthorizedError):
            registry.call(
                "get_user_order_history",
                {},
                context=ToolContext(user=AnonymousUser()),
            )

    def test_order_history_returns_only_context_users_orders(self):
        other_user = User.objects.create_user(
            username="other_tool_user",
            email="other-tool@test.com",
            password="password123",
        )
        own_order = Order.objects.create(
            client=self.user,
            restaurant=self.restaurant,
            status=Order.STATUS_COMPLETED,
            total_price=Decimal("150.00"),
            street="Main Street",
            building="1",
        )
        Order.objects.create(
            client=other_user,
            restaurant=self.restaurant,
            status=Order.STATUS_COMPLETED,
            total_price=Decimal("200.00"),
            street="Other Street",
            building="2",
        )

        result = registry.call(
            "get_user_order_history",
            {},
            context=self.context,
        )

        self.assertEqual(
            [order["id"] for order in result["data"]["orders"]],
            [own_order.id],
        )


# =============================================================
# TOOL ERROR CONTRACT
# =============================================================


class ToolErrorContractTests(TestCase):
    def test_tool_errors_are_tool_errors(self):
        errors = [
            ToolNotFoundError("Not found"),
            ToolValidationError("Invalid input"),
            ToolExecutionError("Execution failed"),
            ToolUnauthorizedError("Unauthorized"),
        ]

        for error in errors:
            self.assertIsInstance(
                error,
                ToolError,
            )


# =============================================================
# VOCABULARY PROVIDER (LOADING AND CACHE)
# =============================================================


class VocabularyProviderTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("ai.services.tool_registry.call")
    def test_vocabulary_is_loaded_from_tools(self, mock_call):
        def tool_response(
            name,
            arguments=None,
            context=None,
        ):
            responses = {
                "get_available_tags": {
                    "data": {
                        "tags": [
                            {"name": "spicy"},
                            {"name": "vegan"},
                        ]
                    }
                },
                "get_available_cuisines": {
                    "data": {
                        "cuisines": [
                            {"name": "Japanese"},
                            {"name": "Italian"},
                        ]
                    }
                },
                "get_available_categories": {
                    "data": {
                        "categories": [
                            {"name": "Sushi"},
                            {"name": "Pasta"},
                        ]
                    }
                },
            }

            return responses[name]

        mock_call.side_effect = tool_response

        provider = VocabularyProvider()
        vocabulary = provider.get()

        self.assertEqual(
            vocabulary,
            {
                "tags": [
                    "spicy",
                    "vegan",
                ],
                "cuisines": [
                    "Japanese",
                    "Italian",
                ],
                "categories": [
                    "Sushi",
                    "Pasta",
                ],
            },
        )

        self.assertEqual(
            mock_call.call_count,
            3,
        )

    @patch("ai.services.tool_registry.call")
    def test_vocabulary_is_cached(self, mock_call):
        mock_call.side_effect = [
            {"data": {"tags": [{"name": "spicy"}]}},
            {"data": {"cuisines": [{"name": "Japanese"}]}},
            {"data": {"categories": [{"name": "Sushi"}]}},
        ]

        provider = VocabularyProvider()

        first_result = provider.get()
        second_result = provider.get()

        self.assertEqual(
            first_result,
            second_result,
        )

        self.assertEqual(
            mock_call.call_count,
            3,
        )

    @patch("ai.services.tool_registry.call")
    def test_vocabulary_falls_back_to_empty_lists_on_tool_error(
        self,
        mock_call,
    ):
        mock_call.side_effect = ToolExecutionError(
            "Vocabulary service unavailable",
        )

        provider = VocabularyProvider()
        vocabulary = provider.get()

        self.assertEqual(
            vocabulary,
            {
                "tags": [],
                "cuisines": [],
                "categories": [],
            },
        )

    @patch("ai.services.tool_registry.call")
    def test_vocabulary_falls_back_on_malformed_tool_response(self, mock_call):
        mock_call.return_value = {"data": {}}

        self.assertEqual(
            VocabularyProvider().get(),
            {"tags": [], "cuisines": [], "categories": []},
        )
        self.assertIsNone(cache.get(VocabularyProvider.CACHE_KEY))

    @patch("ai.services.tool_registry.call")
    def test_each_vocabulary_tool_is_called_with_empty_arguments(
        self,
        mock_call,
    ):
        mock_call.side_effect = [
            {"data": {"tags": [{"name": "spicy"}]}},
            {"data": {"cuisines": [{"name": "Japanese"}]}},
            {"data": {"categories": [{"name": "Sushi"}]}},
        ]

        provider = VocabularyProvider()
        provider.get()

        self.assertEqual(
            mock_call.call_args_list[0].args[0],
            "get_available_tags",
        )

        self.assertEqual(
            mock_call.call_args_list[1].args[0],
            "get_available_cuisines",
        )

        self.assertEqual(
            mock_call.call_args_list[2].args[0],
            "get_available_categories",
        )


# =============================================================
# INTENT EXTRACTOR + VOCABULARY
# =============================================================


class IntentVocabularyIntegrationTests(TestCase):
    @patch("ai.services.GroqClient.chat_completion")
    def test_intent_extractor_receives_authoritative_vocabulary(
        self,
        mock_chat_completion,
    ):
        mock_chat_completion.return_value = {
            "max_price": None,
            "is_vegetarian": None,
            "is_vegan": None,
            "keywords": [],
            "categories": ["Sushi"],
            "cuisines": ["Japanese"],
        }

        extractor = IntentExtractor()

        vocabulary = {
            "tags": [
                "spicy",
                "vegan",
            ],
            "cuisines": [
                "Japanese",
                "Italian",
            ],
            "categories": [
                "Sushi",
                "Pasta",
            ],
        }

        extractor.extract(
            "I want Japanese sushi",
            vocabulary=vocabulary,
        )

        user_content = mock_chat_completion.call_args.kwargs[
            "user_content"
        ]

        self.assertIn(
            "KNOWN VOCABULARY",
            user_content,
        )

        self.assertIn(
            "Japanese",
            user_content,
        )

        self.assertIn(
            "Italian",
            user_content,
        )

        self.assertIn(
            "Sushi",
            user_content,
        )

        self.assertIn(
            "Pasta",
            user_content,
        )

        self.assertIn(
            "spicy",
            user_content,
        )

        self.assertIn(
            "vegan",
            user_content,
        )

    @patch("ai.services.GroqClient.chat_completion")
    def test_intent_extractor_works_without_vocabulary(
        self,
        mock_chat_completion,
    ):
        mock_chat_completion.return_value = {
            "max_price": None,
            "is_vegetarian": None,
            "is_vegan": None,
            "keywords": [],
            "categories": [],
            "cuisines": [],
        }

        extractor = IntentExtractor()
        result = extractor.extract("food")

        self.assertIsInstance(
            result,
            dict,
        )

        mock_chat_completion.assert_called_once()
