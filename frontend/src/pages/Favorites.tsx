import { type FC } from 'react';
import { Link } from 'react-router-dom';
import { useFavorites } from '../context/FavoritesContext';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import { SectionContainer, EmptyState, LoadingState, Alert, Button } from '../components/common';
import type { Restaurant } from '../features/restaurants/types/restaurant.types';

const Favorites: FC = () => {
  const { favorites, isLoading, error } = useFavorites();

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SectionContainer width="page" padding="lg" className="w-full flex-1">
        
        <div className="mb-10 flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b border-border-default pb-6">
          <div className="flex items-center gap-4">
            <h2 className="text-display">Favorites</h2>
            {!isLoading && !error && (
              <span className="text-sm font-medium text-text-secondary bg-surface-muted px-2.5 py-1 rounded-none" aria-live="polite">
                {favorites.length} {favorites.length === 1 ? 'place' : 'places'}
              </span>
            )}
          </div>
        </div>

        {isLoading ? (
          <div className="py-20 flex justify-center">
            <LoadingState message="Loading your favorites..." />
          </div>
        ) : error ? (
          <Alert 
            variant="error" 
            title="Unable to load favorites" 
            message={error} 
            onRetry={() => window.location.reload()} 
          />
        ) : favorites.length === 0 ? (
          <EmptyState
            title="No favorites yet"
            description="You haven't saved any restaurants to your favorites. Discover new places and tap the heart icon to build your personal collection!"
            action={
              <Link to="/">
                <Button variant="primary">
                  Browse restaurants
                </Button>
              </Link>
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {favorites.map((favorite) => (
              <div key={favorite.id}>
                <RestaurantCard restaurant={favorite.restaurant_detail as unknown as Restaurant} />
              </div>
            ))}
          </div>
        )}
        
      </SectionContainer>
    </div>
  );
};

export default Favorites;
