import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import { useSearchParams } from 'react-router-dom';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { Restaurant } from '../features/restaurants/types/restaurant.types';
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
  }
];

const Home: FC = () => {
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get('q') || '';
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
      {/* Main Content: Restaurant Grid & Promotions */}
      <SectionContainer width="page" padding="md" className="flex-1 w-full mt-6">
        
        {/* Promotional Carousel */}
        {!hasSearchQuery && (
           <div className="mb-10 w-full">
              <PromotionCarousel promotions={MOCK_PROMOTIONS} autoScrollInterval={6000} />
           </div>
        )}

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
