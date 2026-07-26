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
  const isValidId = Number.isInteger(numericRestaurantId) && numericRestaurantId > 0;

  const [restaurant, setRestaurant] = useState<RestaurantDetails | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(isValidId);
  const [error, setError] = useState<string | null>(isValidId ? null : 'This restaurant link is not valid.');

  useEffect(() => {
    if (!isValidId) {
      return;
    }
    const controller = new AbortController();

    const loadInitialRestaurant = async () => {
      try {
        const data = await restaurantService.getRestaurantDetails(
          numericRestaurantId,
          controller.signal,
        );
        if (!controller.signal.aborted) {
          setRestaurant(data);
          setError(null);
        }
      } catch {
        if (!controller.signal.aborted) {
          setError('We could not load this restaurant right now. Please try again.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    void loadInitialRestaurant();

    return () => controller.abort();
  }, [isValidId, numericRestaurantId]);

  const reload = useCallback(() => {
    if (!isValidId) return;
    setIsLoading(true);
    setError(null);

    const reloadData = async () => {
      try {
        const data = await restaurantService.getRestaurantDetails(numericRestaurantId);
        setRestaurant(data);
        setError(null);
      } catch {
        setError('We could not load this restaurant right now. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    void reloadData();
  }, [isValidId, numericRestaurantId]);

  return { restaurant, isLoading, error, reload };
};
