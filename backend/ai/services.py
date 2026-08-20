import json
import logging
import requests
from django.conf import settings
from django.db.models import Q
from rest_framework.exceptions import APIException
from restaurants.models import MenuItem

from .serializers import ExtractedIntentSerializer, LLMRecommendationResponseSerializer
from .prompts import INTENT_EXTRACTION_PROMPT, RECOMMENDATION_PROMPT

logger = logging.getLogger(__name__)

class GroqAPIException(APIException):
    status_code = 503
    default_detail = "The recommendation service is temporarily unavailable."
    default_code = "service_unavailable"

class GroqClient:
    def __init__(self):
        self.api_key = getattr(settings, "GROQ_API_KEY", None)
        self.model = getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def chat_completion(self, system_prompt, user_content, temperature=0.0):
        if not self.api_key:
            logger.error("GROQ_API_KEY is not set.")
            raise GroqAPIException()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
            return json.loads(raw_text)
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq network error: {str(e)}")
            raise GroqAPIException()
        except json.JSONDecodeError as e:
            logger.error(f"Groq returned invalid JSON: {str(e)}")
            raise GroqAPIException()
        except Exception as e:
            logger.error(f"Unexpected Groq error: {str(e)}")
            raise GroqAPIException()

class IntentExtractor:
    def __init__(self, client=None):
        self.client = client or GroqClient()

    def extract(self, query: str) -> dict:
        raw_json = self.client.chat_completion(
            system_prompt=INTENT_EXTRACTION_PROMPT,
            user_content=f"USER REQUEST: {query}"
        )
        serializer = ExtractedIntentSerializer(data=raw_json)
        if serializer.is_valid():
            return serializer.validated_data
        logger.warning(f"Extracted intent validation failed: {serializer.errors}")
        return ExtractedIntentSerializer().to_representation({}) # Return empty defaults

class CandidateRetriever:
    def retrieve(self, intent: dict) -> list:
        queryset = MenuItem.objects.filter(is_available=True).select_related('restaurant', 'category').prefetch_related('tags')

        max_price = intent.get("max_price")
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if intent.get("is_vegetarian"):
            queryset = queryset.filter(is_vegetarian=True)
            
        if intent.get("is_vegan"):
            queryset = queryset.filter(is_vegan=True)

        categories = intent.get("categories", [])
        if categories:
            queryset = queryset.filter(category__name__in=categories)

        cuisines = intent.get("cuisines", [])
        if cuisines:
            queryset = queryset.filter(restaurant__cuisine__name__in=cuisines)

        keywords = intent.get("keywords", [])
        if keywords:
            keyword_q = Q()
            for kw in keywords:
                keyword_q |= Q(name__icontains=kw) | Q(description__icontains=kw) | Q(tags__name__icontains=kw)
            queryset = queryset.filter(keyword_q).distinct()

        # Limit to reasonable number to fit in context window
        candidates = queryset.order_by("-restaurant__rating")[:30]
        
        results = []
        for item in candidates:
            results.append({
                "id": item.id,
                "name": item.name,
                "restaurant_name": item.restaurant.name,
                "description": item.description,
                "price": float(item.price),
                "tags": [tag.name for tag in item.tags.all()],
                "is_vegetarian": item.is_vegetarian,
                "is_vegan": item.is_vegan,
                "calories": item.calories
            })
        return results

class CandidateRanker:
    def __init__(self, client=None):
        self.client = client or GroqClient()

    def rank(self, query: str, candidates: list) -> dict:
        if not candidates:
            return {"recommendations": [], "summary": "No candidates available."}
            
        user_content = f"USER REQUEST: {query}\n\nAVAILABLE CANDIDATES:\n{json.dumps(candidates, indent=2)}"
        
        raw_json = self.client.chat_completion(
            system_prompt=RECOMMENDATION_PROMPT,
            user_content=user_content
        )
        
        serializer = LLMRecommendationResponseSerializer(data=raw_json)
        if serializer.is_valid():
            return serializer.validated_data
            
        logger.warning(f"LLM Response schema validation failed: {serializer.errors}")
        raise GroqAPIException()

class RecommendationOrchestrator:
    def __init__(self, client=None):
        self.client = client or GroqClient()
        self.extractor = IntentExtractor(self.client)
        self.retriever = CandidateRetriever()
        self.ranker = CandidateRanker(self.client)

    def process(self, query: str) -> dict:
        logger.info(f"AI Recommend started for query: '{query}'")
        
        # 1. Extract Intent
        intent = self.extractor.extract(query)
        logger.info(f"Extracted Intent: {intent}")
        
        # 2. Retrieve Candidates
        candidates = self.retriever.retrieve(intent)
        logger.info(f"Candidate count retrieved: {len(candidates)}")
        
        if not candidates:
            return {
                "message": "I couldn't find an option that matches all of those requirements.",
                "recommendations": []
            }
            
        # 3. Rank Candidates
        ranking_result = self.ranker.rank(query, candidates)
        raw_recommendations = ranking_result.get("recommendations", [])
        summary = ranking_result.get("summary", "")
        
        # 4. Validate against DB
        valid_ids = [rec["menu_item_id"] for rec in raw_recommendations]
        logger.info(f"LLM Ranked IDs: {valid_ids}")
        
        db_items = MenuItem.objects.filter(id__in=valid_ids, is_available=True).select_related('restaurant', 'category')
        item_map = {item.id: item for item in db_items}
        
        final_recommendations = []
        for rec in raw_recommendations:
            item_id = rec["menu_item_id"]
            if item_id in item_map:
                item = item_map[item_id]
                final_recommendations.append({
                    "menu_item": {
                        "id": item.id,
                        "name": item.name,
                        "price": str(item.price),
                        "restaurant": {
                            "id": item.restaurant.id,
                            "name": item.restaurant.name
                        }
                    },
                    "reason": rec["reason"]
                })
        
        logger.info(f"Final validated recommendations count: {len(final_recommendations)}")
        
        if not final_recommendations:
            return {
                "message": "I couldn't find an option that perfectly matches what you're looking for right now.",
                "recommendations": []
            }
            
        return {
            "message": summary,
            "recommendations": final_recommendations
        }
