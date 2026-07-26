import { useCallback, useEffect, useState } from 'react';
import { restaurantService } from '../api/restaurant.service';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface UseRestaurantDetailsReturn {
  restaurant: RestaurantDetails | null;
  isLoading: boolean;
  error: string | null;
  reload: () => void;
}

export const useRestaurantDetails = (restaurantId?: string): UseRestaurantDetailsReturn => {
  const numericRestaurantId = Number(restaurantId);
  const [restaurant, setRestaurant] = useState<RestaurantDetails | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadRestaurant = useCallback(
    async (signal?: AbortSignal) => {
      if (!Number.isInteger(numericRestaurantId) || numericRestaurantId <= 0) {
        setError('This restaurant link is not valid.');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await restaurantService.getRestaurantDetails(
          numericRestaurantId,
          signal,
        );
        if (!signal?.aborted) {
          setRestaurant(data);
        }
      } catch {
        if (!signal?.aborted) {
          setError('We could not load this restaurant right now. Please try again.');
        }
      } finally {
        if (!signal?.aborted) {
          setIsLoading(false);
        }
      }
    },
    [numericRestaurantId],
  );

  useEffect(() => {
    const controller = new AbortController();
    void loadRestaurant(controller.signal);
    return () => controller.abort();
  }, [loadRestaurant]);

  const reload = useCallback(() => {
    void loadRestaurant();
  }, [loadRestaurant]);

  return { restaurant, isLoading, error, reload };
};
