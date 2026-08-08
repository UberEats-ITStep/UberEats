import { useState, useEffect } from 'react';
import { orderService } from '../../orders/api/order.service';
import type { Review } from '../types/review.types';

export function useEligibleReviewOrder(
  restaurantId: number | undefined, 
  userId: number | undefined,
  reviews: Review[]
) {
  const [eligibleOrderId, setEligibleOrderId] = useState<number | null>(null);
  const [isCheckingEligibility, setIsCheckingEligibility] = useState(false);

  useEffect(() => {
    const checkEligibility = async () => {
      if (!restaurantId || !userId) {
        setEligibleOrderId(null);
        return;
      }

      setIsCheckingEligibility(true);
      try {
        const orderHistory = await orderService.getOrderHistory();
        
        // Find completed orders for this restaurant
        const completedOrders = orderHistory.filter(
          order => order.restaurant === restaurantId && ((order.status as string).toUpperCase() === 'COMPLETED' || order.status === 'Completed')
        );

        // Sort to get the newest first (assuming higher ID or created_at string comparison)
        completedOrders.sort((a, b) => b.id - a.id);

        // Find the first order that does not have an existing review by this user
        const reviewedOrderIds = new Set(
          reviews
            .filter(r => r.client === userId)
            .map(r => r.order)
        );

        const eligible = completedOrders.find(order => !reviewedOrderIds.has(order.id));
        setEligibleOrderId(eligible ? eligible.id : null);
      } catch (err) {
        console.error('Failed to check review eligibility', err);
        setEligibleOrderId(null);
      } finally {
        setIsCheckingEligibility(false);
      }
    };

    void checkEligibility();
  }, [restaurantId, userId, reviews]);

  return {
    eligibleOrderId,
    isCheckingEligibility
  };
}
