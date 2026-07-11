import apiClient from '../../../api/client';
import type { Restaurant } from '../types/restaurant.types';

export const restaurantService = {
  async getRestaurants(signal?: AbortSignal): Promise<Restaurant[]> {
    const response = await apiClient.get<Restaurant[]>('/restaurants/', { signal });
    return response.data;
  },
};