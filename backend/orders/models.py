from django.conf import settings
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
    delivery_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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