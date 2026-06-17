from rest_framework.routers import DefaultRouter
from .views import RestaurantCRUD,CategoryCRUD,MenuItemCRUD

router = DefaultRouter()
router.register("restaurants",RestaurantCRUD)
router.register("categories",CategoryCRUD)
router.register("menuItems",MenuItemCRUD)

urlpatterns = router.urls
