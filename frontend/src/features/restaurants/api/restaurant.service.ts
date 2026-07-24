import apiClient from '../../../api/client';
import type { Restaurant, RestaurantDetails } from '../types/restaurant.types';

export const restaurantService = {
  async getRestaurants(signal?: AbortSignal): Promise<Restaurant[]> {
    const response = await apiClient.get<Restaurant[]>('/restaurants/', { signal });
    return response.data;
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
