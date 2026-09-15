from .models import Order


class OrderHistoryService:
    @staticmethod
    def get_recent_orders(user, limit=10):
        qs = (
            Order.objects.filter(client=user, status=Order.STATUS_COMPLETED)
            .select_related("restaurant")
            .order_by("-created_at")[: max(1, min(limit, 50))]
        )
        return [
            {
                "id": order.id,
                "restaurant": order.restaurant_name_snapshot or order.restaurant.name,
                "total_price": float(order.total_price),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
            }
            for order in qs
        ]