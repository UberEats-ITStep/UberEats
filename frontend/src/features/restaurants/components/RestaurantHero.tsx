import { useState, type FC } from 'react';
import FavoriteButton from '../../favorites/components/FavoriteButton';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface RestaurantHeroProps {
  restaurant: RestaurantDetails;
}

const RestaurantHero: FC<RestaurantHeroProps> = ({ restaurant }) => {
  const [imageError, setImageError] = useState(false);
  const showImage = Boolean(restaurant.image_url) && !imageError;

  return (
    <section className="relative layout-grid min-h-[500px]">
      
      {/* Left Column: Title and details */}
      <div className="col-span-1 md:col-span-4 lg:col-span-5 flex flex-col justify-center order-2 lg:order-1 pt-12 lg:pt-0 pb-8 lg:pb-0 z-10">
        <div className="max-w-xl">
          <div className="mb-6 flex flex-wrap items-center gap-3">
            <span className="text-[10px] font-bold tracking-widest uppercase text-text-muted border border-border-default px-3 py-1">
              {restaurant.cuisine_name}
            </span>
            <span
              className={`text-[10px] font-bold tracking-widest uppercase px-3 py-1 ${
                restaurant.is_open_now 
                  ? 'bg-primary text-surface' 
                  : 'bg-muted text-text-muted'
              }`}
            >
              {restaurant.is_open_now ? 'Open now' : 'Closed'}
            </span>
          </div>
          <div className="mb-6 flex items-center gap-3">
            <h1 className="text-5xl lg:text-7xl font-serif italic tracking-tight text-text-primary leading-none">
              {restaurant.name}
            </h1>
            <FavoriteButton restaurantId={restaurant.id} className="shrink-0" />
          </div>
          {restaurant.description && (
            <p className="max-w-md text-sm leading-relaxed text-text-secondary">
              {restaurant.description}
            </p>
          )}
        </div>
      </div>

      {/* Right Column: Large Magazine-style Media */}
      <div className="col-span-1 md:col-span-4 lg:col-span-7 relative h-72 md:h-96 lg:h-full order-1 lg:order-2 bg-secondary overflow-hidden">
        {showImage ? (
          <img
            src={restaurant.image_url}
            alt={restaurant.name}
            onError={() => setImageError(true)}
            className="absolute inset-0 h-full w-full object-cover"
            loading="eager"
            fetchPriority="high"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-primary">
            <span className="font-serif italic text-3xl opacity-20 text-surface">BiteUp.</span>
          </div>
        )}
      </div>

    </section>
  );
};

export default RestaurantHero;
