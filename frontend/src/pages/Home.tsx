import { useState } from 'react';
import type { FC, ChangeEvent } from 'react';
import RestaurantCard from '../features/restaurants/components/RestaurantCard';
import { mockRestaurants } from '../features/restaurants/mock/restaurants';

const Home: FC = () => {
  const [searchQuery, setSearchQuery] = useState<string>('');

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const filteredRestaurants = mockRestaurants.filter((restaurant) => {
    const query = searchQuery.toLowerCase();
    return (
      restaurant.name.toLowerCase().includes(query) ||
      restaurant.description.toLowerCase().includes(query) ||
      restaurant.categories.some(category => category.toLowerCase().includes(query))
    );
  });

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
            {searchQuery ? `Search results for "${searchQuery}"` : 'Popular near you'}
          </h2>
        </div>

        {/* Data States */}
        {filteredRestaurants.length === 0 ? (
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
