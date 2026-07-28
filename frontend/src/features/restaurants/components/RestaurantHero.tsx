import { useState, type FC } from 'react';
import type { RestaurantDetails } from '../types/restaurant.types';
import { Badge } from '../../../components/common';

export interface RestaurantHeroProps {
  restaurant: RestaurantDetails;
}

const RestaurantHero: FC<RestaurantHeroProps> = ({ restaurant }) => {
  const [imageError, setImageError] = useState(false);
  const showImage = Boolean(restaurant.image_url) && !imageError;

  return (
    <section className="relative min-h-80 overflow-hidden rounded-xl bg-primary shadow-elevated">
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
        <div className="absolute inset-0 bg-gradient-to-tr from-primary via-primary-hover to-accent/30 opacity-60" />
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-primary via-primary/50 to-transparent" />
      <div className="relative flex min-h-80 items-end p-6 sm:p-10">
        <div className="max-w-3xl text-white">
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <Badge variant="brand" size="md">
              {restaurant.cuisine_name}
            </Badge>
            <Badge
              variant={restaurant.is_open_now ? 'success' : 'neutral'}
              size="md"
              className={!restaurant.is_open_now ? 'bg-white/15 text-white border-white/20 backdrop-blur-sm' : ''}
            >
              {restaurant.is_open_now ? 'Open now' : 'Closed'}
            </Badge>
          </div>
          <h1 className="text-display sm:text-5xl text-white">
            {restaurant.name}
          </h1>
          {restaurant.description && (
            <p className="mt-4 max-w-2xl text-base leading-7 text-slate-200 sm:text-lg">
              {restaurant.description}
            </p>
          )}
        </div>
      </div>
    </section>
  );
};

export default RestaurantHero;
