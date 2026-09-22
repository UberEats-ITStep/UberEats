import re

filepath = "backend/reviews/management/commands/seed_reviews.py"
with open(filepath, "r") as f:
    content = f.read()

content = content.replace("client_id=u.idser", "client=user")

with open(filepath, "w") as f:
    f.write(content)
