from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle

from .serializers import AIRecommendationRequestSerializer
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
        result = orchestrator.process(query)
        
        return Response(result)
