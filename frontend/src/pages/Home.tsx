import { useEffect, useMemo, useState, useRef } from 'react';
import type { FC } from 'react';
import { useSearchParams } from 'react-router-dom';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import RestaurantFilters from '../features/restaurants/components/RestaurantFilters';
import type { RestaurantFilterValues } from '../features/restaurants/components/RestaurantFilters';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { Cuisine, Restaurant } from '../features/restaurants/types/restaurant.types';
import { SectionContainer, LoadingState, EmptyState, Alert } from '../components/common';
import EditorialHero from '../features/home/components/EditorialHero';
import { useAuth } from '../hooks/useAuth';

gsap.registerPlugin(ScrollTrigger);

const EMPTY_FILTERS: RestaurantFilterValues = {
  cuisine: '',
  minRating: '',
  ordering: '',
};

const Home: FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
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

  useGSAP(() => {
    if (isLoading || restaurants.length === 0) return;

    let mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", () => {
      // Stagger entrance for featured section
      gsap.fromTo('.restaurant-featured-reveal',
        { y: 30, opacity: 0 },
        { 
          y: 0, opacity: 1, stagger: 0.1, duration: 0.8, ease: 'power2.out',
          scrollTrigger: { trigger: '#restaurants', start: 'top 80%' }
        }
      );
      
      // Batch reveal for standard grid to handle scrolling
      ScrollTrigger.batch('.restaurant-grid-reveal', {
        interval: 0.1, // time window (in seconds) for batching
        batchMax: 4,   // maximum batch size
        onEnter: batch => gsap.fromTo(batch, 
          { y: 30, opacity: 0 },
          { y: 0, opacity: 1, stagger: 0.1, duration: 0.6, ease: 'power2.out', overwrite: true }
        ),
        start: 'top 85%'
      });
    });

    return () => mm.revert();
  }, { scope: containerRef, dependencies: [restaurants, isLoading] });

  const hasFilters = useMemo(() => Object.values(activeFilters).some(Boolean), [activeFilters]);

  const updateFilters = (nextFilters: RestaurantFilterValues) => setFilters(nextFilters);
  const clearFilters = () => setFilters(EMPTY_FILTERS);

  if (isAuthLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <LoadingState message="" />
      </div>
    );
  }

  const featuredRestaurant = restaurants[0];
  const sideRestaurants = restaurants.slice(1, 3);
  const standardRestaurants = restaurants.slice(3);

  return (
    <div ref={containerRef} className="flex min-h-screen flex-col bg-background">
      {!isAuthenticated && <EditorialHero />}
      
      <SectionContainer width="page" padding="lg" className="w-full flex-1" id="restaurants">

        <div className="mb-10 flex flex-col xl:flex-row xl:items-center justify-between gap-6 border-b border-border-default pb-6">
          <div className="flex items-center gap-4">
            <h2 className="text-display">{hasFilters ? 'Restaurant results' : 'Discover'}</h2>
            {!isLoading && !requestError && (
              <span className="text-sm font-medium text-text-secondary bg-surface-muted px-2.5 py-1 rounded-none" aria-live="polite">
                {restaurants.length} {restaurants.length === 1 ? 'place' : 'places'}
              </span>
            )}
          </div>
          <RestaurantFilters values={activeFilters} cuisines={cuisines} onChange={updateFilters} onClear={clearFilters} />
        </div>

        {isLoading ? (
          <div className="py-20 flex justify-center"><LoadingState message="Curating restaurants..." /></div>
        ) : requestError ? (
          <Alert variant="error" title="Unable to load restaurants" message={requestError} onRetry={() => setRetryCount((count) => count + 1)} />
        ) : restaurants.length === 0 ? (
          <EmptyState
            title={hasFilters ? 'No matches found' : 'No restaurants available'}
            description={hasFilters ? 'Try a different search or clear one of your filters.' : 'We are currently expanding in your area. Please check back soon!'}
            action={hasFilters ? <button type="button" onClick={clearFilters} className="text-button text-primary underline decoration-border-focus decoration-2 underline-offset-4 hover:opacity-80">Clear filters</button> : undefined}
          />
        ) : (
          <div className="flex flex-col gap-12">
            
            {/* Top Editorial Section */}
            {restaurants.length > 0 && (
              <div className="layout-grid">
                {/* Featured */}
                <div className="col-span-1 md:col-span-4 lg:col-span-8 restaurant-featured-reveal">
                  <RestaurantCard restaurant={featuredRestaurant} isFeatured={true} />
                </div>
                
                {/* Sidebar stacked */}
                {sideRestaurants.length > 0 && (
                  <div className="col-span-1 md:col-span-4 lg:col-span-4 flex flex-col gap-6 lg:gap-8 justify-between">
                    {sideRestaurants.map(restaurant => (
                      <div className="flex-1 restaurant-featured-reveal" key={restaurant.id}>
                        <RestaurantCard restaurant={restaurant} isFeatured={false} compact={true} />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Standard Grid */}
            {standardRestaurants.length > 0 && (
              <div className="w-full border-t border-border-subtle pt-8">
                <h3 className="text-section-title mb-6">More near you</h3>
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {standardRestaurants.map((restaurant) => (
                    <div key={restaurant.id} className="restaurant-grid-reveal opacity-0">
                      <RestaurantCard restaurant={restaurant} />
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}
      </SectionContainer>
    </div>
  );
};

export default Home;
