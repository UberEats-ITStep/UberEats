from django.urls import path
from .views import RecommendView

app_name = "ai"

urlpatterns = [
    path("recommend/", RecommendView.as_view(), name="recommend"),
]
