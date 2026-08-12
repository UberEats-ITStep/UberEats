import apiClient from '../../../api/client';
import type {
  Cuisine,
  Restaurant,
  RestaurantDetails,
  RestaurantFilters,
} from '../types/restaurant.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const restaurantService = {
  async getRestaurants(filters: RestaurantFilters = {}, signal?: AbortSignal): Promise<Restaurant[]> {
    const params = {
      search: filters.search?.trim() || undefined,
      cuisine: filters.cuisine,
      rating__gte: filters.minRating,
      ordering: filters.ordering || undefined,
    };
    const response = await apiClient.get<Restaurant[] | PaginatedResponse<Restaurant>>('/restaurants/', {
      params,
      signal,
    });
    if (response.data && 'results' in response.data && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    return response.data as Restaurant[];
  },
  async getCuisines(signal?: AbortSignal): Promise<Cuisine[]> {
    const response = await apiClient.get<Cuisine[] | PaginatedResponse<Cuisine>>('/cuisines/', { signal });
    if (response.data && 'results' in response.data && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    return response.data as Cuisine[];
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
