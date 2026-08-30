import { useEffect } from 'react';
import { useOrderDetails } from './useOrderDetails';
import type { OrderStatus } from '../types/order.types';

const ORDER_STATUS_POLL_INTERVAL = 10000;

const isTerminalStatus = (status?: OrderStatus) => {
  return status === 'COMPLETED' || status === 'CANCELLED';
};

export const useOrderTracking = (orderId?: string) => {
  const { order, isLoading, error, backgroundError, reload } = useOrderDetails(orderId);

  useEffect(() => {
    if (!order || isTerminalStatus(order.status)) {
      return;
    }

    const timer = window.setInterval(() => {
      reload(true);
    }, ORDER_STATUS_POLL_INTERVAL);

    return () => window.clearInterval(timer);
  }, [order?.status, reload, order]);

  return {
    order,
    isLoading,
    error,
    backgroundError,
    reload,
  };
};
