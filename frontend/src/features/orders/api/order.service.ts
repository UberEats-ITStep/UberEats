import apiClient from '../../../api/client';
import type { Order } from '../types/order.types';

export const orderService = {
    async getOrderHistory(signal?: AbortSignal): Promise<Order[]> {
        const response = await apiClient.get<Order[]>('/orders/history/', { signal });
        return response.data;
    },
};