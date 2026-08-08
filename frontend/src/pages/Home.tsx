import { useEffect, useMemo, useState } from 'react';
import type { FC } from 'react';
import { useSearchParams } from 'react-router-dom';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import RestaurantFilters from '../features/restaurants/components/RestaurantFilters';
import type { RestaurantFilterValues } from '../features/restaurants/components/RestaurantFilters';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { Cuisine, Restaurant } from '../features/restaurants/types/restaurant.types';
import { SectionContainer, LoadingState, EmptyState, Alert } from '../components/common';
import PromotionCarousel from '../features/home/components/PromotionCarousel';
import type { Promotion } from '../features/home/types/promotion.types';

const MOCK_PROMOTIONS: Promotion[] = [
  {
    id: 1,
    title: 'Free Delivery Weekend',
    description: 'Enjoy free delivery on all orders over $20 this weekend only!',
    ctaText: 'Order Now',
    ctaLink: '/restaurants',
    backgroundColor: 'bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900',
    textColor: 'text-white',
    accentColor: 'text-accent',
    illustrationEmoji: '🛵',
  },
  {
    id: 2,
    title: '20% Off Sushi',
    description: 'Craving sushi? Get a sweet 20% discount on top-rated sushi places.',
    ctaText: 'Find Sushi',
    ctaLink: '/?q=sushi',
    backgroundColor: 'bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900',
    textColor: 'text-white',
    accentColor: 'text-rose-500',
    illustrationEmoji: '🍣',
  },
  {
    id: 3,
    title: 'Summer Deals',
    description: 'Cool down with buy-1-get-1-free ice cream and cold beverages.',
    ctaText: 'Cool Down',
    ctaLink: '/?q=ice',
    backgroundColor: 'bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900',
    textColor: 'text-white',
    accentColor: 'text-sky-400',
    illustrationEmoji: '🍦',
  },
];

const EMPTY_FILTERS: RestaurantFilterValues = {
  cuisine: '',
  minRating: '',
  ordering: '',
};

const Home: FC = () => {
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

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SectionContainer width="page" padding="md" className="mt-6 w-full flex-1">
        {!hasFilters && (
          <div className="mb-10 w-full">
            <PromotionCarousel promotions={MOCK_PROMOTIONS} autoScrollInterval={6000} />
          </div>
        )}

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
