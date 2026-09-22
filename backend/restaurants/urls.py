from .views import CategoryCRUD, CuisineCRUD, MenuItemCRUD, RestaurantViewSet

def register_routes(router):
    router.register("restaurants", RestaurantViewSet, basename="restaurant")
    router.register("categories", CategoryCRUD, basename="category")
    router.register("cuisines", CuisineCRUD, basename="cuisine")
    router.register("menuItems", MenuItemCRUD, basename="menuitem")
    router.register("menu-items", MenuItemCRUD, basename="menuitem-hyphen")

urlpatterns = []
