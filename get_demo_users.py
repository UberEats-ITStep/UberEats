import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
for u in User.objects.filter(email__endswith='biteup.demo').order_by('id')[:5]:
    print(f"Email: {u.email}, Username: {u.username}, First Name: {u.first_name}")
