import { useState, useEffect, useCallback } from 'react';
import type { Review, ReviewPayload } from '../types/review.types';
import { reviewService } from '../api/review.service';

export function useReviews(restaurantId: number | undefined) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReviews = useCallback(async (signal?: AbortSignal) => {
    if (!restaurantId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const data = await reviewService.getReviews(restaurantId, signal);
      setReviews(data);
    } catch (err) {
      const e = err as { name?: string; response?: { data?: { detail?: string } } };
      if (e.name !== 'CanceledError') {
        setError(e.response?.data?.detail || 'Failed to load reviews.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [restaurantId]);

  useEffect(() => {
    const controller = new AbortController();
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadReviews(controller.signal);
    return () => controller.abort();
  }, [loadReviews]);

  const addReview = async (payload: ReviewPayload) => {
    const newReview = await reviewService.createReview(payload);
    setReviews(prev => [newReview, ...prev]);
    return newReview;
  };

  const updateReview = async (reviewId: number, payload: Partial<ReviewPayload>) => {
    const updatedReview = await reviewService.updateReview(reviewId, payload);
    setReviews(prev => prev.map(r => r.id === reviewId ? updatedReview : r));
    return updatedReview;
  };

  const deleteReview = async (reviewId: number) => {
    await reviewService.deleteReview(reviewId);
    setReviews(prev => prev.filter(r => r.id !== reviewId));
  };

  return {
    reviews,
    isLoading,
    error,
    addReview,
    updateReview,
    deleteReview,
    reload: loadReviews
  };
}
