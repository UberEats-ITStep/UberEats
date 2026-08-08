import time
from django.conf import settings
from .models import Order


def simulate_order_lifecycle(order_id):
    """
    Simulates the lifecycle of an order from PENDING to COMPLETED.
    Designed to be easily converted into a Celery @shared_task later.
    """
    transitions = getattr(settings, 'ORDER_SIMULATION_TRANSITIONS', [])
    
    expected_current_status = Order.STATUS_PENDING
    
    for next_status, delay in transitions:
        time.sleep(delay)
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            break
            
        # Stop simulation if order was modified externally
        if order.status != expected_current_status:
            break
            
        order.status = next_status
        order.save(update_fields=['status'])
        
        expected_current_status = next_status
