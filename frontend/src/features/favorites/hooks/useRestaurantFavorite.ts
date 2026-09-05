import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../../../hooks/useAuth';
import { favoritesService } from '../api/favorites.service';

export interface UseRestaurantFavoriteResult {
  isFavorite: boolean;
  favoriteId: number | null;
  isLoading: boolean;
  error: string | null;
  toggleFavorite: () => Promise<void>;
  reload: () => Promise<void>;
}

export const useRestaurantFavorite = (restaurantId?: number): UseRestaurantFavoriteResult => {
  const { isAuthenticated } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteId, setFavoriteId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!restaurantId || !isAuthenticated) {
      setIsFavorite(false);
      setFavoriteId(null);
      return;
    }

    try {
      setError(null);
      const status = await favoritesService.checkFavorite(restaurantId);
      setIsFavorite(Boolean(status.is_favorite));
      setFavoriteId(null);

      if (status.is_favorite) {
        const favorites = await favoritesService.getFavorites();
        const match = favorites.find((entry) => entry.restaurant === restaurantId);
        if (match) {
          setFavoriteId(match.id);
        }
      }
    } catch {
      setError('We could not load your favorite status right now.');
    }
  }, [isAuthenticated, restaurantId]);

  useEffect(() => {
    if (!restaurantId || !isAuthenticated) {
      setIsFavorite(false);
      setFavoriteId(null);
      return;
    }

    const controller = new AbortController();
    const loadFavoriteStatus = async () => {
      setIsLoading(true);
      try {
        const status = await favoritesService.checkFavorite(restaurantId, controller.signal);
        setIsFavorite(Boolean(status.is_favorite));
        setFavoriteId(null);

        if (status.is_favorite) {
          const favorites = await favoritesService.getFavorites(controller.signal);
          const match = favorites.find((entry) => entry.restaurant === restaurantId);
          if (match) {
            setFavoriteId(match.id);
          }
        }
      } catch {
        setError('We could not load your favorite status right now.');
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    void loadFavoriteStatus();
    return () => controller.abort();
  }, [isAuthenticated, restaurantId]);

  const toggleFavorite = useCallback(async () => {
    if (!restaurantId || !isAuthenticated) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (isFavorite && favoriteId) {
        await favoritesService.removeFavorite(favoriteId);
        setIsFavorite(false);
        setFavoriteId(null);
        return;
      }

      const created = await favoritesService.addFavorite(restaurantId);
      setIsFavorite(true);
      setFavoriteId(created.id);
    } catch (favoriteError) {
      const message =
        favoriteError instanceof Error && 'response' in favoriteError
          ? 'This restaurant could not be updated right now.'
          : 'This restaurant could not be updated right now.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [favoriteId, isAuthenticated, isFavorite, restaurantId]);

  return {
    isFavorite,
    favoriteId,
    isLoading,
    error,
    toggleFavorite,
    reload,
  };
};
