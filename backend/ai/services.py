import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from rest_framework.exceptions import APIException

from restaurants.models import MenuItem

from .prompts import INTENT_EXTRACTION_PROMPT, RECOMMENDATION_PROMPT
from .serializers import ExtractedIntentSerializer, LLMRecommendationResponseSerializer
from .tools import registry as tool_registry
from .tools.errors import ToolError
from .user_context import UserContextBuilder

logger = logging.getLogger(__name__)


@dataclass
class RecommendationTrace:
    """Execution details used by evaluation and diagnostics, never API output."""

    query: str
    intent: dict = field(default_factory=dict)
    user_context: dict = field(default_factory=dict)
    candidates: list = field(default_factory=list)
    raw_recommendations: list = field(default_factory=list)
    discarded_recommendations: list = field(default_factory=list)
    final_menu_item_ids: list = field(default_factory=list)
    outcome: str = "pending"

    def as_dict(self) -> dict:
        return {
            "query": self.query,
            "intent": self.intent,
            "user_context": self.user_context,
            "candidates": self.candidates,
            "raw_recommendations": self.raw_recommendations,
            "discarded_recommendations": self.discarded_recommendations,
            "final_menu_item_ids": self.final_menu_item_ids,
            "outcome": self.outcome,
        }


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
            error_body = e.response.text if e.response is not None else "No response body"
            logger.error(f"Groq network error: {str(e)} | Body: {error_body}")
            raise GroqAPIException()
        except json.JSONDecodeError as e:
            logger.error(f"Groq returned invalid JSON: {str(e)}")
            raise GroqAPIException()
        except Exception as e:
            logger.error(f"Unexpected Groq error: {str(e)}")
            raise GroqAPIException()


class VocabularyProvider:
    """
    Builds a short summary of BiteUp's real vocabulary (tags/cuisines/
    categories) via the MCP/tool layer, so intent extraction is grounded
    in what actually exists instead of assumptions baked into the prompt.

    This is the concrete fix for the "AI has no way to discover what
    BiteUp actually contains" problem: a handful of read-only tool calls
    made once per (cached) window, not an agent loop.

    Tool failures never break recommendation: on any ToolError this
    falls back to an empty vocabulary and the pipeline behaves exactly
    as it did before the tool layer existed.
    """

    CACHE_KEY = "ai:vocabulary:v1"
    CACHE_TTL_SECONDS = 300

    def __init__(self, registry=None):
        self.registry = registry or tool_registry

    def get(self) -> dict:
        cached = cache.get(self.CACHE_KEY)
        if cached is not None:
            return cached

        vocabulary = {"tags": [], "cuisines": [], "categories": []}
        try:
            tags = self.registry.call("get_available_tags", {})["data"]["tags"]
            cuisines = self.registry.call("get_available_cuisines", {})["data"]["cuisines"]
            categories = self.registry.call("get_available_categories", {})["data"]["categories"]
            vocabulary = {
                "tags": [t["name"] for t in tags],
                "cuisines": [c["name"] for c in cuisines],
                "categories": [c["name"] for c in categories],
            }
        except (ToolError, KeyError, TypeError) as exc:
            logger.warning(
                "Vocabulary tool call failed or returned malformed data; "
                "falling back to empty vocabulary: %s",
                exc,
            )
            return vocabulary

        cache.set(self.CACHE_KEY, vocabulary, self.CACHE_TTL_SECONDS)
        return vocabulary


class IntentExtractor:
    def __init__(self, client=None):
        self.client = client or GroqClient()

    def extract(self, query: str, vocabulary: Optional[dict] = None) -> dict:
        user_content = f"USER REQUEST: {query}"
        if vocabulary and any(vocabulary.values()):
            user_content += (
                "\n\nKNOWN VOCABULARY (BiteUp's actual tags/cuisines/categories - "
                "prefer these values; do not invent ones that aren't listed):\n"
                f"{json.dumps(vocabulary, ensure_ascii=False)}"
            )

        raw_json = self.client.chat_completion(
            system_prompt=INTENT_EXTRACTION_PROMPT,
            user_content=user_content
        )
        serializer = ExtractedIntentSerializer(data=raw_json)
        if serializer.is_valid():
            return serializer.validated_data
        logger.warning(f"Extracted intent validation failed: {serializer.errors}")
        return ExtractedIntentSerializer().to_representation({}) # Return empty defaults


class CandidateRetriever:
    def retrieve(self, intent: dict) -> list:
        queryset = (
            MenuItem.objects.filter(
                is_available=True,
                restaurant__is_active=True,
            )
            .select_related('restaurant', 'category')
            .prefetch_related('tags')
        )

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
        candidates = queryset.order_by("-restaurant__rating", "-id")[:50]
        
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

    def rank(
        self,
        query: str,
        candidates: list,
        user_context: dict,
    ) -> dict:

        if not candidates:
            return {
                "recommendations": [],
                "summary": "No candidates available.",
            }

        user_content = (
            f"CURRENT USER REQUEST:\n{query}\n\n"
            f"AUTHORITATIVE USER CONTEXT:\n"
            f"{json.dumps(user_context, ensure_ascii=False, indent=2)}\n\n"
            f"AVAILABLE CANDIDATES:\n"
            f"{json.dumps(candidates, ensure_ascii=False, indent=2)}"
        )

        raw_json = self.client.chat_completion(
            system_prompt=RECOMMENDATION_PROMPT,
            user_content=user_content,
        )

        serializer = LLMRecommendationResponseSerializer(
            data=raw_json
        )

        if serializer.is_valid():
            return serializer.validated_data

        logger.warning(
            "LLM Response schema validation failed: %s",
            serializer.errors,
        )

        raise GroqAPIException()


class RecommendationOrchestrator:
    def __init__(self, client=None):
        self.client = client or GroqClient()
        self.extractor = IntentExtractor(self.client)
        self.retriever = CandidateRetriever()
        self.ranker = CandidateRanker(self.client)
        self.user_context_builder = UserContextBuilder()
        self.vocabulary_provider = VocabularyProvider()

    def process(self, query: str, user) -> dict:
        result, _ = self.process_with_trace(query=query, user=user)
        return result

    def process_with_trace(self, query: str, user) -> tuple[dict, dict]:
        trace = RecommendationTrace(query=query)
        logger.info(f"AI Recommend started for query: '{query}'")

        vocabulary = self.vocabulary_provider.get()

        intent = self.extractor.extract(query, vocabulary=vocabulary)
        trace.intent = intent
        logger.info(f"Extracted Intent: {intent}")

        user_context = self.user_context_builder.build(user)
        trace.user_context = user_context
        logger.info(
            "Built user context (has_history=%s, completed_orders=%s)",
            user_context["has_history"],
            user_context["completed_order_count"],
        )

        candidates = self.retriever.retrieve(intent)
        trace.candidates = candidates
        logger.info(f"Candidate count retrieved: {len(candidates)}")

        if not candidates:
            trace.outcome = "no_candidates"
            return {
                "message": "I couldn't find an option that matches all of those requirements.",
                "recommendations": []
            }, trace.as_dict()

        ranking_result = self.ranker.rank(
            query,
            candidates,
            user_context,
        )

        raw_recommendations = ranking_result.get(
            "recommendations",
            []
        )
        trace.raw_recommendations = raw_recommendations

        summary = ranking_result.get("summary", "")

        candidate_ids = {
            candidate["id"]
            for candidate in candidates
        }
        valid_ids = []
        seen_ids = set()
        for rec in raw_recommendations:
            item_id = rec["menu_item_id"]
            if item_id not in candidate_ids:
                trace.discarded_recommendations.append({
                    "menu_item_id": item_id,
                    "reason": "not_in_candidate_pool",
                })
                continue
            if item_id in seen_ids:
                trace.discarded_recommendations.append({
                    "menu_item_id": item_id,
                    "reason": "duplicate_menu_item",
                })
                continue
            if len(valid_ids) == 4:
                trace.discarded_recommendations.append({
                    "menu_item_id": item_id,
                    "reason": "result_limit_exceeded",
                })
                continue
            seen_ids.add(item_id)
            valid_ids.append(item_id)

        db_items = (
            MenuItem.objects
            .filter(
                id__in=valid_ids,
                is_available=True,
            )
            .select_related("restaurant", "category")
        )

        item_map = {
            item.id: item
            for item in db_items
        }

        final_recommendations = []

        for rec in raw_recommendations:
            item_id = rec["menu_item_id"]

            if item_id in item_map and item_id in valid_ids:
                item = item_map[item_id]

                final_recommendations.append({
                    "menu_item": {
                        "id": item.id,
                        "name": item.name,
                        "price": str(item.price),
                        "restaurant": {
                            "id": item.restaurant.id,
                            "name": item.restaurant.name,
                        },
                    },
                    "reason": rec["reason"],
                })

        trace.final_menu_item_ids = [
            recommendation["menu_item"]["id"]
            for recommendation in final_recommendations
        ]

        if not final_recommendations:
            trace.outcome = "no_valid_recommendations"
            return {
                "message": (
                    "I couldn't find an option that perfectly "
                    "matches what you're looking for right now."
                ),
                "recommendations": [],
            }, trace.as_dict()

        trace.outcome = "recommended"
        return {
            "message": summary,
            "recommendations": final_recommendations,
        }, trace.as_dict()
