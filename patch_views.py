import re

filepath = "backend/favorites/views.py"
with open(filepath, "r") as f:
    content = f.read()

# Add import
content = content.replace(
    'from rest_framework import mixins, permissions, status, viewsets',
    'from rest_framework import mixins, permissions, status, viewsets\nfrom rest_framework.throttling import ScopedRateThrottle'
)

# Add throttle classes
throttle_addition = """    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "favorites"
"""

content = content.replace(
    '    serializer_class = FavoriteSerializer\n    permission_classes = [permissions.IsAuthenticated]\n',
    throttle_addition
)

with open(filepath, "w") as f:
    f.write(content)
