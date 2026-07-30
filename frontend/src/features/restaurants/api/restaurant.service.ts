import apiClient from '../../../api/client';
import type { Restaurant, RestaurantDetails } from '../types/restaurant.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const restaurantService = {
  async getRestaurants(signal?: AbortSignal): Promise<Restaurant[]> {
    const response = await apiClient.get<Restaurant[] | PaginatedResponse<Restaurant>>('/restaurants/', { signal });
    if (response.data && 'results' in response.data && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    return response.data as Restaurant[];
  },
  async getRestaurantDetails(
    restaurantId: number,
    signal?: AbortSignal,
  ): Promise<RestaurantDetails> {
    const response = await apiClient.get<RestaurantDetails>(
      `/restaurants/${restaurantId}/`,
      { signal },
    );
    return response.data;
  },
};
