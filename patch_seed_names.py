import re

filepath = "backend/reviews/management/commands/seed_reviews.py"
with open(filepath, "r") as f:
    content = f.read()

names_list = """UKRAINIAN_NAMES = [
    "Oleksandr", "Andrii", "Artem", "Bohdan", "Danylo", "Denys", "Dmytro", "Ivan", 
    "Maksym", "Mykhailo", "Nazar", "Oleksii", "Pavlo", "Petro", "Roman", "Serhii", 
    "Taras", "Vadym", "Volodymyr", "Yaroslav", "Anastasiia", "Anna", "Bohdana", 
    "Daria", "Kateryna", "Khrystyna", "Liudmyla", "Mariia", "Marta", "Nataliia", 
    "Oksana", "Olena", "Polina", "Svitlana", "Tetiana", "Valentyna", "Viktoriia", 
    "Yana", "Yelyzaveta", "Yuliia", "Alina", "Diana", "Iryna", "Karina", "Lesia", 
    "Sofia", "Solomiia", "Veronika", "Vlada", "Zoriana"
]

TEMPLATES = {"""

content = content.replace("TEMPLATES = {", names_list)

defaults_replacement = """                    defaults={
                        'username': UKRAINIAN_NAMES[(i - 1) % len(UKRAINIAN_NAMES)],"""

content = re.sub(r"                    defaults=\{\n                        'username': email\.split\('@'\)\[0\],", defaults_replacement, content)

with open(filepath, "w") as f:
    f.write(content)
