import apiClient from '../../../api/client';
import type { Order } from '../types/order.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const orderService = {
    async getOrderHistory(signal?: AbortSignal): Promise<Order[]> {
        const response = await apiClient.get<Order[] | PaginatedResponse<Order>>('/orders/history/', { signal });
        if (response.data && 'results' in response.data && Array.isArray(response.data.results)) {
            return response.data.results;
        }
        return response.data as Order[];
    },
    
    async checkout(delivery_address: string): Promise<Order> {
        const response = await apiClient.post<Order>('/orders/checkout/', { delivery_address });
        return response.data;
    },
};