import re

filepath = "backend/favorites/views.py"
with open(filepath, "r") as f:
    content = f.read()

# Replace the heavy check query
check_optimization = """        # Verify the restaurant exists and is active (to match existing 404 behavior)
        restaurant_exists = Restaurant.objects.filter(pk=restaurant_id, is_active=True).exists()
        if not restaurant_exists:
            from django.http import Http404
            raise Http404()

        # Optimize the favorite check to avoid unnecessary joins from get_queryset()
        favorite = Favorite.objects.filter(
            user=self.request.user,
            restaurant_id=restaurant_id
        ).values("id").first()

        return Response(
            {
                "restaurant": restaurant_id,
                "is_favorite": favorite is not None,
                "favorite_id": favorite["id"] if favorite else None,
            }
        )"""

content = re.sub(
    r'        restaurant = get_object_or_404\([\s\S]*?favorite\.id if favorite else None,\n            \}\n        \)',
    check_optimization,
    content
)

with open(filepath, "w") as f:
    f.write(content)
