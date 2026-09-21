import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from restaurants.models import MenuItem

from .models import RecommendationEvent
from .serializers import (
    AIRecommendationRequestSerializer,
    RecommendationEventSerializer,
)
from .services import RecommendationOrchestrator

class RecommendView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'ai_recommend'

    def post(self, request, *args, **kwargs):
        serializer = AIRecommendationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['query']
        orchestrator = RecommendationOrchestrator()
        result = orchestrator.process(
            query=query,
            user=request.user,
        )
        request_id = uuid.uuid4()
        RecommendationEvent.objects.bulk_create([
            RecommendationEvent(
                request_id=request_id,
                user=request.user,
                menu_item_id=recommendation["menu_item"]["id"],
                event_type=RecommendationEvent.EventType.SERVED,
                query=query,
                position=position,
            )
            for position, recommendation in enumerate(
                result["recommendations"], start=1
            )
        ])
        result["recommendation_request_id"] = str(request_id)
        return Response(result)


class RecommendationEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = RecommendationEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            menu_item = MenuItem.objects.get(
                pk=data["menu_item_id"],
                is_available=True,
                restaurant__is_active=True,
            )
        except MenuItem.DoesNotExist:
            return Response(
                {"detail": "The recommended menu item is unavailable."},
                status=400,
            )
        RecommendationEvent.objects.create(
            request_id=data["request_id"],
            user=request.user,
            menu_item=menu_item,
            event_type=data["event_type"],
            position=data.get("position"),
        )
        return Response(status=204)
