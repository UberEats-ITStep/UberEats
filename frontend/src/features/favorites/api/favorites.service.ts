import apiClient from '../../../api/client';
import type { Favorite, FavoriteCheckResponse } from '../types/favorite.types';

export const favoritesService = {
  async getFavorites(signal?: AbortSignal): Promise<Favorite[]> {
    const response = await apiClient.get<Favorite[]>('/favorites/', { signal });
    return response.data;
  },

  async checkFavorite(restaurantId: number, signal?: AbortSignal): Promise<FavoriteCheckResponse> {
    const response = await apiClient.get<FavoriteCheckResponse>('/favorites/check/', {
      params: { restaurant: restaurantId },
      signal,
    });
    return response.data;
  },

  async addFavorite(restaurantId: number): Promise<Favorite> {
    const response = await apiClient.post<Favorite>('/favorites/', { restaurant: restaurantId });
    return response.data;
  },

  async removeFavorite(favoriteId: number): Promise<void> {
    await apiClient.delete(`/favorites/${favoriteId}/`);
  },
};
