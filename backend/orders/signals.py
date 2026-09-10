import threading
from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order
from .simulation import simulate_order_lifecycle


@receiver(post_save, sender=Order)
def trigger_order_simulation(sender, instance, created, **kwargs):
    """
    Triggers the order lifecycle simulation when a new order is created,
    but only if the application is running in DEBUG mode.
    Ensures the simulation thread starts after transaction commits.
    """
    if created and getattr(settings, 'DEBUG', False):
        def start_simulation():
            threading.Thread(
                target=simulate_order_lifecycle,
                args=(instance.id,),
                daemon=True
            ).start()

        transaction.on_commit(start_simulation)
