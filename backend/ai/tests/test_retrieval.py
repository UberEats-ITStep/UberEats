from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from restaurants.models import Restaurant, Category, MenuItem, MenuTag
from ai.services import CandidateRetriever

class CandidateRetrieverTests(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name="Test Rest")
        self.category = Category.objects.create(name="Burgers")
        
        self.item1 = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Classic Burger",
            description="A very satisfying and hearty burger.",
            price=Decimal("150.00"),
            is_available=True,
            is_vegetarian=False,
        )
        self.item2 = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Veggie Burger",
            description="Light but filling plant-based option.",
            price=Decimal("120.00"),
            is_available=True,
            is_vegetarian=True,
            is_vegan=True,
        )
        
        # We manually mock the embedding field if we want, or just leave it null
        # In a real test with pgvector we could set it to [0.1]*384
        self.retriever = CandidateRetriever()

    def test_hard_constraints_preserved(self):
        # Even with semantic query, if price is filtered, it must be respected
        intent = {
            "max_price": 130,
            "semantic_query": "A hearty burger", # Matches item1 conceptually
        }
        
        with patch('ai.services.TextEmbedding') as mock_embedding:
            # Mock the embedding return
            mock_model = MagicMock()
            mock_model.embed.return_value = [[0.1] * 384]
            mock_embedding.return_value = mock_model
            
            # Should only return Veggie Burger because Classic Burger is 150 > 130
            # Wait, since embedding is null on item1 and item2, the query will exclude them!
            # Let's add a fake embedding to item2
            self.item2.embedding = [0.1] * 384
            self.item2.save()
            
            candidates = self.retriever.retrieve(intent)
            
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["name"], "Veggie Burger")

    def test_lexical_fallback(self):
        intent = {
            "keywords": ["hearty"],
            "semantic_query": "Something hearty"
        }
        
        # Force the semantic retrieval to fail (e.g. fastembed not installed or exception)
        with patch('ai.services.TextEmbedding', side_effect=Exception("Model failed")):
            candidates = self.retriever.retrieve(intent)
            # Should fallback to lexical and find Classic Burger
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0]["name"], "Classic Burger")

    def test_surprise_me_empty_intent(self):
        intent = {}
        # Empty intent should return candidates ordered by rating/id, no exception
        candidates = self.retriever.retrieve(intent)
        self.assertEqual(len(candidates), 2)
