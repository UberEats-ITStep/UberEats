import uuid

from django.db import models


class RecommendationEvent(models.Model):
	class EventType(models.TextChoices):
		SERVED = "served", "Recommendation served"
		CLICKED = "clicked", "Recommendation clicked"
		ADDED_TO_CART = "added_to_cart", "Recommendation added to cart"
		ORDERED = "ordered", "Recommendation ordered"

	request_id = models.UUIDField(default=uuid.uuid4, db_index=True)
	user = models.ForeignKey(
		"users.User",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="recommendation_events",
	)
	menu_item = models.ForeignKey(
		"restaurants.MenuItem",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="recommendation_events",
	)
	event_type = models.CharField(max_length=20, choices=EventType.choices)
	query = models.CharField(max_length=500, blank=True, default="")
	position = models.PositiveSmallIntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [models.Index(fields=["request_id", "event_type"])]
