from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.decorators import action
from rest_framework.response import Response

from restaurants.models import Restaurant

from .models import Favorite
from .serializers import FavoriteSerializer


class FavoriteViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "favorites"

    def get_queryset(self):
        return (
            Favorite.objects.filter(user=self.request.user, restaurant__is_active=True)
            .select_related("restaurant", "restaurant__cuisine")
            .prefetch_related("restaurant__opening_hours")
        )

    @action(detail=False, methods=["get"])
    def check(self, request):
        restaurant_id = request.query_params.get("restaurant")
        if not restaurant_id:
            return Response(
                {"restaurant": "This query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            restaurant_id = int(restaurant_id)
            if restaurant_id <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {"restaurant": "Enter a valid restaurant ID."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify the restaurant exists and is active (to match existing 404 behavior)
        restaurant_exists = Restaurant.objects.filter(pk=restaurant_id, is_active=True).exists()
        if not restaurant_exists:
            from django.http import Http404
            raise Http404()

        # Optimize the favorite check to avoid unnecessary joins from get_queryset()
        favorite = Favorite.objects.filter(
            user=self.request.user,
            restaurant_id=restaurant_id
        ).values("id").first()

        return Response(
            {
                "restaurant": restaurant_id,
                "is_favorite": favorite is not None,
                "favorite_id": favorite["id"] if favorite else None,
            }
        )
