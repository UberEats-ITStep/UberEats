from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.menu_item.name} x {self.quantity}'
