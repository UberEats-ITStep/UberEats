from rest_framework.routers import DefaultRouter
from .views import CategoryCRUD, CuisineCRUD, MenuItemCRUD, RestaurantViewSet

router = DefaultRouter()
router.register("restaurants", RestaurantViewSet, basename="restaurant")
router.register("categories", CategoryCRUD, basename="category")
router.register("cuisines", CuisineCRUD, basename="cuisine")
router.register("menuItems", MenuItemCRUD, basename="menuitem")

urlpatterns = router.urls
