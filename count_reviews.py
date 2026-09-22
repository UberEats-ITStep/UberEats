import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from reviews.models import Review
print("Reviews currently in DB:", Review.objects.count())
