import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import MenuItemCard from '../features/restaurants/components/MenuItemCard';
import { restaurantService } from '../features/restaurants/api/restaurant.service';
import type { RestaurantDetails as RestaurantDetailsData } from '../features/restaurants/types/restaurant.types';

const RestaurantDetails: FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const numericRestaurantId = Number(restaurantId);
  const [restaurant, setRestaurant] = useState<RestaurantDetailsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [requestError, setRequestError] = useState<string | null>(null);

  const loadRestaurant = useCallback(
    async (signal?: AbortSignal) => {
      await Promise.resolve();

      if (!Number.isInteger(numericRestaurantId) || numericRestaurantId <= 0) {
        setRequestError('This restaurant link is not valid.');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setRequestError(null);

      try {
        const data = await restaurantService.getRestaurantDetails(
          numericRestaurantId,
          signal,
        );
        if (!signal?.aborted) {
          setRestaurant(data);
        }
      } catch {
        if (!signal?.aborted) {
          setRequestError('We could not load this restaurant right now. Please try again.');
        }
      } finally {
        if (!signal?.aborted) {
          setIsLoading(false);
        }
      }
    },
    [numericRestaurantId],
  );

  useEffect(() => {
    const controller = new AbortController();

    const loadInitialRestaurant = async () => {
      await Promise.resolve();
      void loadRestaurant(controller.signal);
    };

    void loadInitialRestaurant();
    return () => controller.abort();
  }, [loadRestaurant]);

  if (isLoading) {
    return (
      <div className="py-24 text-center" role="status">
        <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-[#FF8C00]" />
        <p className="text-gray-600">Loading restaurant and menu...</p>
      </div>
    );
  }

  if (requestError || !restaurant) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-red-100 bg-red-50 px-6 py-14 text-center" role="alert">
        <h1 className="text-2xl font-bold text-[#0B132B]">Restaurant unavailable</h1>
        <p className="mt-3 text-gray-600">{requestError}</p>
        <div className="mt-6 flex flex-wrap justify-center gap-3">
          <button
            type="button"
            onClick={() => void loadRestaurant()}
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

  const menuItemCount = restaurant.categories.reduce(
    (total, category) => total + category.menu_items.length,
    0,
  );

  return (
    <div className="pb-16">
      <Link
        to="/"
        className="mb-5 inline-flex items-center text-sm font-semibold text-gray-600 transition-colors hover:text-[#0B132B]"
      >
        ← All restaurants
      </Link>

      <section className="relative min-h-80 overflow-hidden rounded-3xl bg-[#0B132B]">
        {restaurant.image_url && (
          <img
            src={restaurant.image_url}
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-45"
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0B132B] via-[#0B132B]/50 to-transparent" />
        <div className="relative flex min-h-80 items-end p-6 sm:p-10">
          <div className="max-w-3xl text-white">
            <div className="mb-3 flex flex-wrap gap-2 text-sm font-semibold">
              <span className="rounded-full bg-[#FF8C00] px-3 py-1 text-[#0B132B]">
                {restaurant.cuisine_name}
              </span>
              <span className="rounded-full bg-white/15 px-3 py-1 backdrop-blur-sm">
                {restaurant.is_open_now ? 'Open now' : 'Closed'}
              </span>
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
              {restaurant.name}
            </h1>
            {restaurant.description && (
              <p className="mt-4 max-w-2xl text-base leading-7 text-gray-100 sm:text-lg">
                {restaurant.description}
              </p>
            )}
          </div>
        </div>
      </section>

      <section
        aria-label="Restaurant information"
        className="relative z-10 mx-4 -mt-5 grid gap-4 rounded-2xl border border-gray-200 bg-white p-5 shadow-md sm:grid-cols-2 lg:mx-8 lg:grid-cols-4"
      >
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Rating</p>
          <p className="mt-1 font-bold text-[#0B132B]">
            <span className="text-[#FF8C00]">★</span>{' '}
            {restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}
            {restaurant.review_count > 0 && (
              <span className="ml-1 font-normal text-gray-500">
                ({restaurant.review_count})
              </span>
            )}
          </p>
        </div>
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Delivery</p>
          <p className="mt-1 font-bold text-[#0B132B]">
            {restaurant.delivery_time != null
              ? `${restaurant.delivery_time} min`
              : 'Time unavailable'}
          </p>
        </div>
        <div className="sm:col-span-2">
          <p className="text-xs font-bold uppercase tracking-wider text-gray-500">Address</p>
          <p className="mt-1 font-bold text-[#0B132B]">
            {restaurant.address || 'Address unavailable'}
          </p>
        </div>
      </section>

      <main className="mt-12">
        <div className="flex flex-col gap-5 border-b border-gray-200 pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="font-bold uppercase tracking-widest text-[#FF8C00]">Explore</p>
            <h2 className="mt-1 text-3xl font-extrabold text-[#0B132B]">Our menu</h2>
          </div>
          {restaurant.categories.length > 0 && (
            <nav aria-label="Menu categories" className="flex gap-2 overflow-x-auto pb-1">
              {restaurant.categories.map((category) => (
                <a
                  key={category.id}
                  href={`#category-${category.id}`}
                  className="whitespace-nowrap rounded-full bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-[#0B132B] hover:text-white"
                >
                  {category.name}
                </a>
              ))}
            </nav>
          )}
        </div>

        {menuItemCount === 0 ? (
          <div className="mt-8 rounded-2xl bg-gray-50 px-6 py-16 text-center">
            <h2 className="text-xl font-bold text-[#0B132B]">The menu is being prepared</h2>
            <p className="mt-2 text-gray-600">
              This restaurant has no menu items available yet. Please check back soon.
            </p>
          </div>
        ) : (
          <div className="space-y-12 pt-9">
            {restaurant.categories.map((category) => (
              <section
                key={category.id}
                id={`category-${category.id}`}
                className="scroll-mt-24"
              >
                <div className="mb-5 flex items-baseline justify-between gap-4">
                  <h2 className="text-2xl font-extrabold text-[#0B132B]">
                    {category.name}
                  </h2>
                  <span className="text-sm text-gray-500">
                    {category.menu_items.length}{' '}
                    {category.menu_items.length === 1 ? 'item' : 'items'}
                  </span>
                </div>

                {category.menu_items.length === 0 ? (
                  <div className="rounded-2xl bg-gray-50 px-5 py-8 text-gray-600">
                    Nothing is available in {category.name} right now.
                  </div>
                ) : (
                  <div className="grid gap-5 lg:grid-cols-2">
                    {category.menu_items.map((item) => (
                      <MenuItemCard key={item.id} item={item} />
                    ))}
                  </div>
                )}
              </section>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default RestaurantDetails;
