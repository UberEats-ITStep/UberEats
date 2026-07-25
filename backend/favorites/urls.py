from .views import FavoriteViewSet


def register_routes(router):
    router.register("favorites", FavoriteViewSet, basename="favorite")


urlpatterns = []
