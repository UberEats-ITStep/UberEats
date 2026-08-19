import { useCallback, useEffect, useState } from 'react';
import { orderService } from '../api/order.service';
import type { Order } from '../types/order.types';

export const useOrderDetails = (orderId?: string) => {
  const numericOrderId = Number(orderId);
  const isValidId = Number.isInteger(numericOrderId) && numericOrderId > 0;
  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(isValidId);
  const [error, setError] = useState<string | null>(
    isValidId ? null : 'This order link is not valid.',
  );

  const reload = useCallback(async () => {
    if (!isValidId) return;
    setIsLoading(true);
    setError(null);
    try {
      setOrder(await orderService.getOrderDetails(numericOrderId));
    } catch {
      setError('We could not find this order or you do not have access to it.');
    } finally {
      setIsLoading(false);
    }
  }, [isValidId, numericOrderId]);

  useEffect(() => {
    const controller = new AbortController();
    const loadInitialOrder = async () => {
      try {
        const data = await orderService.getOrderDetails(numericOrderId, controller.signal);
        if (!controller.signal.aborted) {
          setOrder(data);
          setError(null);
        }
      } catch {
        if (!controller.signal.aborted) {
          setError('We could not find this order or you do not have access to it.');
        }
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    };

    if (isValidId) void loadInitialOrder();
    return () => controller.abort();
  }, [isValidId, numericOrderId]);

  return { order, isLoading, error, reload: () => void reload() };
};
