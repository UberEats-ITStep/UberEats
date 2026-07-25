import { useState, type FC } from 'react';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface RestaurantHeroProps {
  restaurant: RestaurantDetails;
}

const RestaurantHero: FC<RestaurantHeroProps> = ({ restaurant }) => {
  const [imageError, setImageError] = useState(false);
  const showImage = Boolean(restaurant.image_url) && !imageError;

  return (
    <section className="relative min-h-80 overflow-hidden rounded-3xl bg-[#0B132B]">
      {showImage ? (
        <img
          src={restaurant.image_url}
          alt={restaurant.name}
          onError={() => setImageError(true)}
          className="absolute inset-0 h-full w-full object-cover opacity-45"
          loading="eager"
          fetchPriority="high"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-tr from-[#0B132B] via-[#172344] to-[#FF8C00]/30 opacity-60" />
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
  );
};

export default RestaurantHero;
