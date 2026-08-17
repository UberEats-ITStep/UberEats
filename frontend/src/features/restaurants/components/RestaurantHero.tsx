import { useState, type FC } from 'react';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface RestaurantHeroProps {
  restaurant: RestaurantDetails;
}

const RestaurantHero: FC<RestaurantHeroProps> = ({ restaurant }) => {
  const [imageError, setImageError] = useState(false);
  const showImage = Boolean(restaurant.image_url) && !imageError;

  return (
    <section className="relative min-h-80 overflow-hidden rounded-none border border-border-default bg-card">
      {showImage ? (
        <img
          src={restaurant.image_url}
          alt={restaurant.name}
          onError={() => setImageError(true)}
          className="absolute inset-0 h-full w-full object-cover grayscale opacity-30"
          loading="eager"
          fetchPriority="high"
        />
      ) : (
        <div className="absolute inset-0 bg-primary opacity-10" />
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
      <div className="relative flex min-h-80 items-end p-6 sm:p-12">
        <div className="max-w-3xl">
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <span className="text-xs font-medium tracking-widest uppercase text-text-primary border border-text-primary px-3 py-1">
              {restaurant.cuisine_name}
            </span>
            <span
              className={`text-xs font-medium tracking-widest uppercase px-3 py-1 ${
                restaurant.is_open_now 
                  ? 'bg-text-primary text-surface' 
                  : 'bg-muted text-text-muted border border-border-default'
              }`}
            >
              {restaurant.is_open_now ? 'Open now' : 'Closed'}
            </span>
          </div>
          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight text-text-primary mb-4">
            {restaurant.name}
          </h1>
          {restaurant.description && (
            <p className="max-w-2xl text-lg leading-relaxed text-text-secondary font-serif italic">
              {restaurant.description}
            </p>
          )}
        </div>
      </div>
    </section>
  );
};

export default RestaurantHero;
