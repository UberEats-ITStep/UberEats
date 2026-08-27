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

    async getOrderDetails(orderId: number, signal?: AbortSignal): Promise<Order> {
        const response = await apiClient.get<Order>(`/orders/${orderId}/`, { signal });
        return response.data;
    },
    
    async checkout(payload: {
        street: string;
        building: string;
        apartment?: string;
        entrance?: string;
        floor?: number | null;
        delivery_notes?: string;
        contact_phone?: string;
        delivery_latitude?: string;
        delivery_longitude?: string;
    }): Promise<Order> {
        const response = await apiClient.post<Order>('/orders/checkout/', payload);
        return response.data;
    },
};
