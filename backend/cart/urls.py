from .views import CartViewSet, CartItemViewSet

def register_routes(router):
    router.register("carts", CartViewSet, basename="cart")
    router.register("cart-items", CartItemViewSet, basename="cartitem")

urlpatterns = []