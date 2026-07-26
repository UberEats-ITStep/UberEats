import { useCallback, useEffect, useState } from 'react';
import type { FC, ChangeEvent } from 'react';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { Restaurant } from '../features/restaurants/types/restaurant.types';
import { SectionContainer, Input, LoadingState, EmptyState, Alert } from '../components/common';

const Home: FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [requestError, setRequestError] = useState<string | null>(null);

  const loadRestaurants = useCallback(async () => {
    setIsLoading(true);
    setRequestError(null);

    try {
      const data = await restaurantService.getRestaurants();
      setRestaurants(data);
    } catch {
      setRequestError('We could not load restaurants right now. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    const loadInitialRestaurants = async () => {
      try {
        const data = await restaurantService.getRestaurants(controller.signal);
        if (!controller.signal.aborted) {
          setRestaurants(data);
        }
      } catch {
        if (!controller.signal.aborted) {
          setRequestError('We could not load restaurants right now. Please try again.');
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    void loadInitialRestaurants();

    return () => controller.abort();
  }, []);

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const normalizedSearchQuery = searchQuery.trim().toLowerCase();
  const filteredRestaurants = restaurants.filter((r) => {
    const query = normalizedSearchQuery;
    return (
      (r.name || '').toLowerCase().includes(query) ||
      (r.description || '').toLowerCase().includes(query) ||
      (r.cuisine_name || '').toLowerCase().includes(query)
    );
  });
  const hasSearchQuery = normalizedSearchQuery.length > 0;

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Hero Section */}
      <section className="border-b border-border-default bg-surface py-16 px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-display mb-4 tracking-tight">
            Discover restaurants near you
          </h1>
          <p className="text-body mb-8 text-lg">
            Get your favorite food delivered directly to your door.
          </p>

          {/* Search UI */}
          <div className="mx-auto max-w-xl">
            <Input
              type="text"
              placeholder="Search restaurants or cuisines..."
              aria-label="Search restaurants or cuisines"
              value={searchQuery}
              onChange={handleSearchChange}
              className="text-center shadow-subtle"
            />
          </div>
        </div>
      </section>

      {/* Main Content: Restaurant Grid */}
      <SectionContainer width="page" padding="md" className="flex-1 w-full">
        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-section-title">
            {hasSearchQuery ? `Search results for "${searchQuery}"` : 'Popular near you'}
          </h2>
        </div>

        {/* Data States */}
        {isLoading ? (
          <LoadingState message="Loading restaurants near you..." />
        ) : requestError ? (
          <Alert
            variant="error"
            title="Unable to load restaurants"
            message={requestError}
            onRetry={() => void loadRestaurants()}
          />
        ) : restaurants.length === 0 ? (
          <EmptyState
            title="No restaurants available"
            description="We are currently expanding in your area. Please check back soon!"
          />
        ) : filteredRestaurants.length === 0 ? (
          <EmptyState
            title="No matches found"
            description={`We couldn't find any restaurants matching "${searchQuery}". Try searching for a different name or cuisine.`}
          />
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filteredRestaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        )}
      </SectionContainer>
    </div>
  );
};

export default Home;
