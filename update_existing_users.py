import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

UKRAINIAN_NAMES = [
    "Oleksandr", "Andrii", "Artem", "Bohdan", "Danylo", "Denys", "Dmytro", "Ivan", 
    "Maksym", "Mykhailo", "Nazar", "Oleksii", "Pavlo", "Petro", "Roman", "Serhii", 
    "Taras", "Vadym", "Volodymyr", "Yaroslav", "Anastasiia", "Anna", "Bohdana", 
    "Daria", "Kateryna", "Khrystyna", "Liudmyla", "Mariia", "Marta", "Nataliia", 
    "Oksana", "Olena", "Polina", "Svitlana", "Tetiana", "Valentyna", "Viktoriia", 
    "Yana", "Yelyzaveta", "Yuliia", "Alina", "Diana", "Iryna", "Karina", "Lesia", 
    "Sofia", "Solomiia", "Veronika", "Vlada", "Zoriana"
]

DEMO_USER_DOMAIN = "biteup.demo"
DEMO_USER_PREFIX = "demo_reviewer_"
DEMO_USER_COUNT = 15

updated_count = 0
for i in range(1, DEMO_USER_COUNT + 1):
    email = f"{DEMO_USER_PREFIX}{i:02d}@{DEMO_USER_DOMAIN}"
    new_username = UKRAINIAN_NAMES[(i - 1) % len(UKRAINIAN_NAMES)]
    updated = User.objects.filter(email=email).update(username=new_username)
    updated_count += updated
    
print(f"Updated {updated_count} existing demo users.")
