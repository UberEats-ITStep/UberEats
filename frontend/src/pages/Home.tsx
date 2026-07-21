import { useCallback, useEffect, useState } from 'react';
import type { FC, ChangeEvent } from 'react';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { Restaurant } from '../features/restaurants/types/restaurant.types';

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
    const restaurant = r as Restaurant & { cuisine_name?: string };
    const query = normalizedSearchQuery;
    return (
      (restaurant.name || '').toLowerCase().includes(query) ||
      (restaurant.description || '').toLowerCase().includes(query) ||
      (restaurant.categories && restaurant.categories.some(category => category.toLowerCase().includes(query))) ||
      (restaurant.cuisine_name && restaurant.cuisine_name.toLowerCase().includes(query))
    );
  });
  const hasSearchQuery = normalizedSearchQuery.length > 0;

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Hero Section */}
      <section className="bg-gray-50 py-16 px-4 sm:px-6 lg:px-8 border-b border-gray-200">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 tracking-tight mb-4">
            Discover restaurants near you
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            Get your favorite food delivered directly to your door.
          </p>

          {/* Search UI */}
          <div className="flex flex-col sm:flex-row items-center justify-center max-w-xl mx-auto space-y-3 sm:space-y-0 sm:space-x-3">
            <input
              type="text"
              placeholder="Search for restaurants, cuisines, or dishes"
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 text-center"
            />
          </div>
        </div>
      </section>

      {/* Main Content: Restaurant Grid */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full">
        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            {hasSearchQuery ? `Search results for "${searchQuery}"` : 'Popular near you'}
          </h2>
        </div>

        {/* Data States */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 text-center text-gray-600" role="status">
            <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-green-600" />
            <p>Loading restaurants near you...</p>
          </div>
        ) : requestError ? (
          <div className="rounded-lg bg-red-50 px-6 py-10 text-center" role="alert">
            <p className="text-gray-700">{requestError}</p>
            <button
              type="button"
              onClick={() => void loadRestaurants()}
              className="mt-4 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            >
              Try again
            </button>
          </div>
        ) : restaurants.length === 0 ? (
          <div className="text-center py-20 text-gray-500 bg-gray-50 rounded-lg">
            No restaurants are available yet. Please check back soon.
          </div>
        ) : filteredRestaurants.length === 0 ? (
          <div className="text-center py-20 text-gray-500 bg-gray-50 rounded-lg">
            No restaurants found matching your search.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredRestaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;
