import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ai.services import CandidateRetriever

intent = {
    "semantic_query": "something sweet and crispy",
    "keywords": ["sweet"],
    "is_vegan": True
}

retriever = CandidateRetriever()
candidates = retriever.retrieve(intent)

print("FOUND CANDIDATES:", len(candidates))
for c in candidates[:3]:
    print(f"- {c['name']} (Price: {c['price']}) - {c['description']} (Vegan: {c['is_vegan']})")

