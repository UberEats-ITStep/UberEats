import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from restaurants.models import Restaurant
print("Total:", Restaurant.objects.count())
print("Active:", Restaurant.objects.filter(is_active=True).count())
