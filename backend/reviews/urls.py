from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

def register_routes(router: DefaultRouter):
    router.register(r'reviews', ReviewViewSet, basename='review')
