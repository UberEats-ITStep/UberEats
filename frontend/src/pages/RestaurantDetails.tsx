import type { FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useRestaurantDetails } from '../features/restaurants/hooks/useRestaurantDetails';
import RestaurantHero from '../features/restaurants/components/RestaurantHero';
import RestaurantStats from '../features/restaurants/components/RestaurantStats';
import CategoryNavbar from '../features/restaurants/components/CategoryNavbar';
import MenuSection from '../features/restaurants/components/MenuSection';

const RestaurantDetails: FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const { restaurant, isLoading, error, reload } = useRestaurantDetails(restaurantId);

  if (isLoading) {
    return (
      <div className="py-24 text-center" role="status">
        <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-[#FF8C00]" />
        <p className="text-gray-600">Loading restaurant and menu...</p>
      </div>
    );
  }

  if (error || !restaurant) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-red-100 bg-red-50 px-6 py-14 text-center" role="alert">
        <h1 className="text-2xl font-bold text-[#0B132B]">Restaurant unavailable</h1>
        <p className="mt-3 text-gray-600">{error}</p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <button
            type="button"
            onClick={reload}
            className="rounded-lg bg-[#0B132B] px-5 py-2.5 font-semibold text-white transition-colors hover:bg-[#172344]"
          >
            Try again
          </button>
          <Link
            to="/"
            className="rounded-lg border border-gray-300 bg-white px-5 py-2.5 font-semibold text-[#0B132B] transition-colors hover:bg-gray-50"
          >
            Browse restaurants
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-16">
      <Link
        to="/"
        className="mb-5 inline-flex items-center text-sm font-semibold text-gray-600 transition-colors hover:text-[#0B132B]"
      >
        ← All restaurants
      </Link>

      <RestaurantHero restaurant={restaurant} />
      <RestaurantStats restaurant={restaurant} />

      <main className="mt-12">
        <div className="flex flex-col gap-5 border-b border-gray-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="font-bold uppercase tracking-widest text-[#FF8C00]">Explore</p>
            <h2 className="mt-1 text-3xl font-extrabold text-[#0B132B]">Our menu</h2>
          </div>
          <CategoryNavbar categories={restaurant.categories} />
        </div>

        <MenuSection categories={restaurant.categories} />
      </main>
    </div>
  );
};

export default RestaurantDetails;
