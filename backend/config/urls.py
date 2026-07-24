"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter, APIRootView
from rest_framework.reverse import reverse

from restaurants.urls import register_routes as register_restaurants_routes
from cart.urls import register_routes as register_cart_routes
from reviews.urls import register_routes as register_reviews_routes

class CustomAPIRootView(APIRootView):
    """
    Custom API Root that injects the modular endpoints (like orders) 
    that are built using simple APIViews rather than ViewSets.
    """
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Inject standard path-based routes into the API Root
        response.data['orders-history'] = reverse('order_history', request=request)
        response.data['orders-checkout'] = reverse('order_checkout', request=request)
        return response

class GlobalRouter(DefaultRouter):
    APIRootView = CustomAPIRootView

# We use a single global DefaultRouter to ensure all modular viewsets
# are registered and exposed together in one unified DRF API Root (/api/).
# Apps define a `register_routes(router)` function to register their own
# endpoints, keeping URL configuration modular and separated.
router = GlobalRouter()

register_restaurants_routes(router)
register_cart_routes(router)
register_reviews_routes(router)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('users.urls')),
    path('api/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
