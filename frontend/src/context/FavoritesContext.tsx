import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import type { ReactNode } from 'react';
import { favoritesService } from '../features/favorites/api/favorites.service';
import type { Favorite } from '../features/favorites/types/favorite.types';
import { useAuth } from '../hooks/useAuth';

interface FavoritesContextType {
  favorites: Favorite[];
  isLoading: boolean;
  error: string | null;
  toggleFavorite: (restaurantId: number) => Promise<void>;
  isFavorite: (restaurantId: number) => boolean;
  getFavoriteId: (restaurantId: number) => number | null;
}

const FavoritesContext = createContext<FavoritesContextType | undefined>(undefined);

export const FavoritesProvider = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // To prevent rapid repeated clicks from creating conflicting mutations
  const [mutatingSet, setMutatingSet] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!isAuthenticated) {
      setFavorites([]);
      return;
    }

    const controller = new AbortController();
    const loadFavorites = async () => {
      setIsLoading(true);
      try {
        const data = await favoritesService.getFavorites(controller.signal);
        setFavorites(data);
        setError(null);
      } catch (err: unknown) {
        if (!controller.signal.aborted) {
          setError('Could not load favorites.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    void loadFavorites();
    return () => controller.abort();
  }, [isAuthenticated]);

  const isFavorite = useCallback((restaurantId: number) => {
    return favorites.some(f => f.restaurant === restaurantId);
  }, [favorites]);

  const getFavoriteId = useCallback((restaurantId: number) => {
    const fav = favorites.find(f => f.restaurant === restaurantId);
    return fav ? fav.id : null;
  }, [favorites]);

  const toggleFavorite = useCallback(async (restaurantId: number) => {
    if (!isAuthenticated || mutatingSet.has(restaurantId)) return;
    
    setMutatingSet(prev => new Set(prev).add(restaurantId));
    
    const favId = getFavoriteId(restaurantId);
    const wasFavorite = !!favId;
    
    try {
      if (wasFavorite && favId) {
        await favoritesService.removeFavorite(favId);
        setFavorites(prev => prev.filter(f => f.id !== favId));
      } else {
        const created = await favoritesService.addFavorite(restaurantId);
        setFavorites(prev => [...prev, created]);
      }
      setError(null);
    } catch (err) {
      throw err;
    } finally {
      setMutatingSet(prev => {
        const next = new Set(prev);
        next.delete(restaurantId);
        return next;
      });
    }
  }, [isAuthenticated, mutatingSet, getFavoriteId]);

  const value = useMemo(() => ({
    favorites,
    isLoading,
    error,
    toggleFavorite,
    isFavorite,
    getFavoriteId
  }), [favorites, isLoading, error, toggleFavorite, isFavorite, getFavoriteId]);

  return (
    <FavoritesContext.Provider value={value}>
      {children}
    </FavoritesContext.Provider>
  );
};

export const useFavorites = () => {
  const context = useContext(FavoritesContext);
  if (context === undefined) {
    throw new Error('useFavorites must be used within a FavoritesProvider');
  }
  return context;
};
