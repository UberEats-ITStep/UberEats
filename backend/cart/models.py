from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="cart",
    )
    
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} cart"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    menu_item = models.ForeignKey(
        "restaurants.MenuItem",
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "menu_item")

    def __str__(self):
        return f"{self.menu_item} x{self.quantity}"