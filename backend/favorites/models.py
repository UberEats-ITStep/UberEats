from django.conf import settings
from django.db import models

from restaurants.models import Restaurant


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,   
        related_name="favorites",
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "restaurant"],
                name="unique_user_restaurant_favorite",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.restaurant}"
