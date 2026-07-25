from django.shortcuts import render
from .models import Favorite
from .serializers import FavoriteSerializer
from rest_framework import viewsets,permissions
# Create your views here.

class FavoriteCRUD(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)