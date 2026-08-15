import { useEffect, useMemo, useState } from 'react';
import type { FC } from 'react';
import { useSearchParams } from 'react-router-dom';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import RestaurantFilters from '../features/restaurants/components/RestaurantFilters';
import type { RestaurantFilterValues } from '../features/restaurants/components/RestaurantFilters';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { Cuisine, Restaurant } from '../features/restaurants/types/restaurant.types';
import { SectionContainer, LoadingState, EmptyState, Alert } from '../components/common';
import EditorialHero from '../features/home/components/EditorialHero';
import { useAuth } from '../hooks/useAuth';

const EMPTY_FILTERS: RestaurantFilterValues = {
  cuisine: '',
  minRating: '',
  ordering: '',
};

const Home: FC = () => {
  const { isAuthenticated, isLoading: isAuthLoading } = useAuth();
  const [searchParams] = useSearchParams();
  const [filters, setFilters] = useState<RestaurantFilterValues>(EMPTY_FILTERS);
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [cuisines, setCuisines] = useState<Cuisine[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [requestError, setRequestError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const activeFilters = useMemo(() => ({
    ...filters,
    search: searchParams.get('q') ?? '',
  }), [filters, searchParams]);

  useEffect(() => {
    const controller = new AbortController();
    void restaurantService.getCuisines(controller.signal)
      .then(setCuisines)
      .catch(() => undefined);
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setIsLoading(true);
      setRequestError(null);

      try {
        const data = await restaurantService.getRestaurants({
          search: activeFilters.search,
          cuisine: activeFilters.cuisine ? Number(activeFilters.cuisine) : undefined,
          minRating: activeFilters.minRating ? Number(activeFilters.minRating) : undefined,
          ordering: activeFilters.ordering,
        }, controller.signal);
        setRestaurants(data);
      } catch {
        if (!controller.signal.aborted) {
          setRequestError('We could not load restaurants right now. Please try again.');
        }
      } finally {
        if (!controller.signal.aborted) setIsLoading(false);
      }
    }, 350);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [activeFilters, retryCount]);

  const hasFilters = useMemo(() => Object.values(activeFilters).some(Boolean), [activeFilters]);

  const updateFilters = (nextFilters: RestaurantFilterValues) => {
    setFilters(nextFilters);
  };

  const clearFilters = () => {
    setFilters(EMPTY_FILTERS);
  };

  if (isAuthLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState message="" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {!isAuthenticated && <EditorialHero />}
      
      <SectionContainer width="page" padding="md" className="w-full flex-1" id="restaurants">

        <div className="mb-6 flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b border-border-default pb-4">
          <div className="flex items-center gap-4">
            <h2 className="text-section-title">{hasFilters ? 'Restaurant results' : 'Popular near you'}</h2>
            {!isLoading && !requestError && (
              <span className="text-sm font-medium text-text-secondary bg-surface-muted px-2.5 py-1 rounded-md" aria-live="polite">
                {restaurants.length} {restaurants.length === 1 ? 'restaurant' : 'restaurants'}
              </span>
            )}
          </div>
          
          <RestaurantFilters values={activeFilters} cuisines={cuisines} onChange={updateFilters} onClear={clearFilters} />
        </div>

        {isLoading ? (
          <LoadingState message="Finding restaurants for you..." />
        ) : requestError ? (
          <Alert variant="error" title="Unable to load restaurants" message={requestError} onRetry={() => setRetryCount((count) => count + 1)} />
        ) : restaurants.length === 0 ? (
          <EmptyState
            title={hasFilters ? 'No matches found' : 'No restaurants available'}
            description={hasFilters ? 'Try a different search or clear one of your filters.' : 'We are currently expanding in your area. Please check back soon!'}
            action={hasFilters ? <button type="button" onClick={clearFilters} className="text-button text-primary underline decoration-accent decoration-2 underline-offset-4">Clear filters</button> : undefined}
          />
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {restaurants.map((restaurant) => <RestaurantCard key={restaurant.id} restaurant={restaurant} />)}
          </div>
        )}
      </SectionContainer>
    </div>
  );
};

export default Home;
