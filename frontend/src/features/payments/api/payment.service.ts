import apiClient from '../../../api/client';

export const paymentService = {
  async createIntent(orderId: number): Promise<{ client_secret: string }> {
    const response = await apiClient.post<{ client_secret: string }>('/payments/create-intent/', {
      order_id: orderId,
    });
    return response.data;
  },

  async reportFailure(orderId: number, errorMessage?: string): Promise<{ status: string; detail: string }> {
    const response = await apiClient.post<{ status: string; detail: string }>('/payments/payment-failed/', {
      order_id: orderId,
      error_message: errorMessage,
    });
    return response.data;
  },
};
