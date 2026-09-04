from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from restaurants.models import MenuItem, Restaurant


class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_PREPARING = 'PREPARING'
    STATUS_READY = 'READY'
    STATUS_DELIVERING = 'DELIVERING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'PENDING'),
        (STATUS_ACCEPTED, 'ACCEPTED'),
        (STATUS_PREPARING, 'PREPARING'),
        (STATUS_READY, 'READY'),
        (STATUS_DELIVERING, 'DELIVERING'),
        (STATUS_COMPLETED, 'COMPLETED'),
        (STATUS_CANCELLED, 'CANCELLED'),
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries',
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    delivery_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    delivery_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    street = models.CharField(max_length=255)
    building = models.CharField(max_length=20)

    apartment = models.CharField(max_length=20, blank=True, default='')
    entrance = models.CharField(max_length=20, blank=True, default='')
    floor = models.PositiveSmallIntegerField(null=True, blank=True)

    delivery_notes = models.TextField(max_length=500, blank=True, default='')
    contact_phone = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    # Snapshot of restaurant name at the time of order creation
    restaurant_name_snapshot = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        delivery_latitude__isnull=True,
                        delivery_longitude__isnull=True,
                    )
                    | models.Q(
                        delivery_latitude__isnull=False,
                        delivery_longitude__isnull=False,
                    )
                ),
                name='order_delivery_coordinates_together',
            ),
        ]
    def clean(self):
        super().clean()
        if (self.delivery_latitude is None) != (self.delivery_longitude is None):
            missing_field = "delivery_longitude" if self.delivery_longitude is None else "delivery_latitude"
            raise ValidationError({
                missing_field: "Delivery latitude and longitude must both be set, or both be empty."
            })

    def __str__(self):
        return f'Order #{self.id} - {self.client.email}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    # Snapshot of menu item name at the time of purchase
    menu_item_name_snapshot = models.CharField(max_length=255, blank=True, default='')
    # Snapshot of restaurant name at the time of purchase
    restaurant_name_snapshot = models.CharField(max_length=255, blank=True, default='')

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        # Prefer the snapshot name for historical safety; fall back to live relation
        name = self.menu_item_name_snapshot or (self.menu_item.name if self.menu_item else '')
        return f'{name} x {self.quantity}'
