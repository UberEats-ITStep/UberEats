import json
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from decimal import Decimal

from restaurants.models import Restaurant, Cuisine, Category, MenuItem, MenuTag
from ai.services import GroqAPIException

User = get_user_model()

class AIRecommendTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pwd', role='CLIENT', is_verified=True)
        self.url = reverse('ai:recommend')
        
        # Setup basic data
        self.cuisine = Cuisine.objects.create(name='Japanese')
        self.restaurant = Restaurant.objects.create(name='Sushi Place', cuisine=self.cuisine)
        self.category = Category.objects.create(name='Sushi')
        self.tag_spicy = MenuTag.objects.create(name='spicy')
        
        self.item1 = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Spicy Tuna Roll',
            description='Very spicy',
            price=Decimal('150.00'),
            is_available=True,
            is_vegetarian=False
        )
        self.item1.tags.add(self.tag_spicy)
        
        self.item2 = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name='Avocado Roll',
            description='Fresh avocado',
            price=Decimal('100.00'),
            is_available=True,
            is_vegetarian=True,
            is_vegan=True
        )

    def test_unauthenticated(self):
        response = self.client.post(self.url, {"query": "sushi"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('ai.services.GroqClient.chat_completion')
    def test_successful_recommendation(self, mock_groq):
        self.client.force_authenticate(user=self.user)
        
        # Mock Intent Extract
        # Mock Ranking
        mock_groq.side_effect = [
            {"max_price": 200, "is_vegetarian": True}, # Intent
            {
                "recommendations": [{"menu_item_id": self.item2.id, "reason": "Vegetarian and under 200."}],
                "summary": "Here is your roll."
            }
        ]
        
        response = self.client.post(self.url, {"query": "vegetarian sushi under 200"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['message'], "Here is your roll.")
        self.assertEqual(len(data['recommendations']), 1)
        self.assertEqual(data['recommendations'][0]['menu_item']['id'], self.item2.id)

    @patch('ai.services.GroqClient.chat_completion')
    def test_empty_candidates_skips_ranking(self, mock_groq):
        self.client.force_authenticate(user=self.user)
        
        # Mock Intent Extract to something impossible (price under 1)
        mock_groq.side_effect = [{"max_price": 1}]
        
        response = self.client.post(self.url, {"query": "cheap food"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Ranking should not be called, so side_effect with 1 item is fine.
        self.assertEqual(mock_groq.call_count, 1)
        self.assertEqual(response.json()['recommendations'], [])
        
    @patch('ai.services.GroqClient.chat_completion')
    def test_hallucinated_id_discarded(self, mock_groq):
        self.client.force_authenticate(user=self.user)
        
        mock_groq.side_effect = [
            {}, # Intent (no filters)
            {
                "recommendations": [
                    {"menu_item_id": 9999, "reason": "Hallucinated"},
                    {"menu_item_id": self.item1.id, "reason": "Valid"}
                ],
                "summary": "Done."
            }
        ]
        
        response = self.client.post(self.url, {"query": "food"})
        data = response.json()
        
        # 9999 should be discarded
        self.assertEqual(len(data['recommendations']), 1)
        self.assertEqual(data['recommendations'][0]['menu_item']['id'], self.item1.id)

    @patch('ai.services.requests.post')
    def test_groq_timeout_handled(self, mock_post):
        import requests
        self.client.force_authenticate(user=self.user)
        
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        response = self.client.post(self.url, {"query": "food"})
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
