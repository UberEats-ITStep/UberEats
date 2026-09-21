from django.urls import path
from .views import RecommendationEventView, RecommendView

app_name = "ai"

urlpatterns = [
    path("recommend/", RecommendView.as_view(), name="recommend"),
    path("recommendation-events/", RecommendationEventView.as_view(), name="recommendation-events"),
]
