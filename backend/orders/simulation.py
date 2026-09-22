import time
import logging
from django.conf import settings
from django.db import connection, close_old_connections
from .models import Order

logger = logging.getLogger(__name__)


def simulate_order_lifecycle(order_id):
    """
    Simulates the lifecycle of an order from PENDING to COMPLETED.
    Designed to be easily converted into a Celery @shared_task later.
    """
    transitions = getattr(settings, 'ORDER_SIMULATION_TRANSITIONS', [])
    expected_current_status = Order.STATUS_PENDING
    
    close_old_connections()
    logger.info(f"[Simulation] Starting order simulation for Order #{order_id}")

    try:
        for next_status, delay in transitions:
            time.sleep(delay)
            close_old_connections()

            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                logger.warning(f"[Simulation] Order #{order_id} does not exist. Halting simulation.")
                break

            # Stop simulation if order was cancelled or declined
            if order.status in (Order.STATUS_CANCELLED, Order.STATUS_DECLINED):
                logger.info(f"[Simulation] Order #{order_id} was {order.status}. Halting simulation.")
                break

            # Stop simulation if payment failed or canceled
            if hasattr(order, 'payment') and order.payment.status in ('failed', 'canceled'):
                logger.info(f"[Simulation] Order #{order_id} payment was {order.payment.status}. Halting simulation.")
                break

            # Stop simulation if order was modified externally
            if order.status != expected_current_status:
                logger.info(
                    f"[Simulation] Order #{order_id} status changed from {expected_current_status} "
                    f"to {order.status}. Halting simulation."
                )
                break

            order.status = next_status
            order.save(update_fields=['status'])
            logger.info(f"[Simulation] Order #{order_id} transitioned to {next_status}")

            expected_current_status = next_status
    except Exception as e:
        logger.error(f"[Simulation] Error during simulation for order #{order_id}: {e}", exc_info=True)
    finally:
        connection.close()
