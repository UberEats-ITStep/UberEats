# urls.py
from rest_framework.routers import DefaultRouter
from .views import FavoriteCRUD

router = DefaultRouter()
router.register("favorites", FavoriteCRUD, basename="favorite")

urlpatterns = router.urls