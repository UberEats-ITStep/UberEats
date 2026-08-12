import apiClient from '../../../api/client';
import type { Review, ReviewPayload, PaginatedReviews } from '../types/review.types';

export const reviewService = {
  async getReviews(restaurantId: number, signal?: AbortSignal): Promise<Review[]> {
    const response = await apiClient.get<Review[] | PaginatedReviews>(`/reviews/`, {
      params: { restaurant: restaurantId },
      signal,
    });
    
    // The backend uses DjangoFilterBackend, if paginated it returns PaginatedReviews
    if (response.data && 'results' in response.data && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    
    return response.data as Review[];
  },

  async createReview(payload: ReviewPayload): Promise<Review> {
    const response = await apiClient.post<Review>('/reviews/', payload);
    return response.data;
  },

  async updateReview(reviewId: number, payload: Partial<ReviewPayload>): Promise<Review> {
    const response = await apiClient.patch<Review>(`/reviews/${reviewId}/`, payload);
    return response.data;
  },

  async deleteReview(reviewId: number): Promise<void> {
    await apiClient.delete(`/reviews/${reviewId}/`);
  }
};
