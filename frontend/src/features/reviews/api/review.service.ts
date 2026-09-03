import apiClient from '../../../api/client';
import type { Review, ReviewPayload, PaginatedReviews } from '../types/review.types';

export const reviewService = {
  async getReviews(restaurantId: number, page = 1, signal?: AbortSignal): Promise<PaginatedReviews> {
    const response = await apiClient.get<Review[] | PaginatedReviews>(`/reviews/`, {
      params: { restaurant: restaurantId, page },
      signal,
    });

    if (Array.isArray(response.data)) {
      return {
        count: response.data.length,
        next: null,
        previous: null,
        results: response.data,
      };
    }

    return response.data;
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
