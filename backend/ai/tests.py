import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
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

from ai.services import GroqAPIException
from ai.user_context import UserContextBuilder


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

        # ---------------------------------------------------------
        # Cuisine
        # ---------------------------------------------------------

        self.cuisine = Cuisine.objects.create(
            name="Japanese"
        )

        self.italian_cuisine = Cuisine.objects.create(
            name="Italian"
        )

        # ---------------------------------------------------------
        # Restaurants
        # ---------------------------------------------------------

        self.restaurant = Restaurant.objects.create(
            name="Sushi Place",
            cuisine=self.cuisine,
        )

        self.italian_restaurant = Restaurant.objects.create(
            name="Italian Place",
            cuisine=self.italian_cuisine,
        )

        # ---------------------------------------------------------
        # Categories
        # ---------------------------------------------------------

        self.category = Category.objects.create(
            name="Sushi"
        )

        self.pasta_category = Category.objects.create(
            name="Pasta"
        )

        # ---------------------------------------------------------
        # Tags
        # ---------------------------------------------------------

        self.tag_spicy = MenuTag.objects.create(
            name="spicy"
        )

        # ---------------------------------------------------------
        # Menu items
        # ---------------------------------------------------------

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

    @patch("ai.services.GroqClient.chat_completion")
    def test_successful_recommendation(self, mock_groq):
        self.client.force_authenticate(
            user=self.user
        )

        mock_groq.side_effect = [
            # -----------------------------------------------------
            # Groq call #1 - Intent extraction
            # -----------------------------------------------------
            {
                "max_price": 200,
                "is_vegetarian": True,
                "is_vegan": None,
                "keywords": [],
                "categories": ["Sushi"],
                "cuisines": ["Japanese"],
            },

            # -----------------------------------------------------
            # Groq call #2 - Candidate ranking
            # -----------------------------------------------------
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

        # Two Groq calls:
        # 1. intent
        # 2. ranking
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

        # Only Intent Extraction should call Groq.
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
            # Intent
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },

            # Ranking
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

        # Hallucinated ID must be discarded.
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

        # Both users currently have no history.
        # Their contexts should be independently generated.
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
            # -----------------------------------------------------
            # Intent extraction
            # -----------------------------------------------------
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },

            # -----------------------------------------------------
            # Personalized ranking
            # -----------------------------------------------------
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

        # Second Groq request is CandidateRanker.
        ranking_call = mock_groq.call_args_list[1]

        user_content = ranking_call.kwargs[
            "user_content"
        ]

        # The ranking prompt must receive all three parts.
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
            # Intent
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },

            # Personalized ranking
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
    # "I DON'T KNOW WHAT I WANT"
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
            # Intent extraction should produce no hard constraints.
            {
                "max_price": None,
                "is_vegetarian": None,
                "is_vegan": None,
                "keywords": [],
                "categories": [],
                "cuisines": [],
            },

            # Ranking
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
            # -----------------------------------------------------
            # Current request:
            #
            # "I want vegan sushi under 300 UAH"
            #
            # Explicit constraints must be extracted.
            # -----------------------------------------------------
            {
                "max_price": 300,
                "is_vegetarian": None,
                "is_vegan": True,
                "keywords": [],
                "categories": ["Sushi"],
                "cuisines": ["Japanese"],
            },

            # -----------------------------------------------------
            # Ranking
            # -----------------------------------------------------
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

        # Verify that ranking received the current request.
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
    # CURRENT QUERY MUST NOT BE REPLACED BY USER CONTEXT
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