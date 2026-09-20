import re

filepath = "backend/reviews/management/commands/seed_reviews.py"
with open(filepath, "r") as f:
    content = f.read()

content = content.replace("client=u", "client_id=u.id")

# add print in dry run
content = content.replace(
    "total_synthetic_orders += missing\n                total_reviews_created += missing",
    "total_synthetic_orders += missing\n                total_reviews_created += missing\n                self.stdout.write(f'[DRY RUN] Would create {missing} reviews for {restaurant.name} (target: {target}, existing seeded: {seeded_reviews_count})')"
)

with open(filepath, "w") as f:
    f.write(content)
