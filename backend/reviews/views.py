from rest_framework import viewsets, permissions
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["restaurant"]

    def get_queryset(self):
        return Review.objects.all().select_related('client', 'client__profile', 'restaurant', 'order')
    
    @transaction.atomic
    def perform_create(self, serializer):
        super().perform_create(serializer)

    @transaction.atomic
    def perform_update(self, serializer):
        super().perform_update(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
