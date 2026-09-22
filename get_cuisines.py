import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from restaurants.models import Cuisine
print([c.name for c in Cuisine.objects.all()])
