import { useState, type FC } from 'react';
import { Link } from 'react-router-dom';
import type { Restaurant } from '../types/restaurant.types';

interface RestaurantCardProps {
  restaurant: Restaurant;
}

const RestaurantCard: FC<RestaurantCardProps> = ({ restaurant }) => {
  const [imageError, setImageError] = useState(false);
  const showPlaceholder = !restaurant.image_url || imageError;

  return (
    <Link
      to={`/restaurants/${restaurant.id}`}
      className="group block overflow-hidden rounded-none border border-border-default bg-card transition-all duration-300 hover:border-border-focus focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-1"
      aria-label={`View ${restaurant.name} menu`}
    >
      {/* Image container with fixed aspect ratio */}
      <div className="relative h-56 w-full overflow-hidden bg-muted border-b border-border-default">
        {showPlaceholder ? (
          <div className="flex h-full w-full flex-col items-center justify-center bg-primary p-4 text-center">
            <span className="text-surface font-serif italic text-2xl tracking-wide opacity-50">
              BiteUp.
            </span>
          </div>
        ) : (
          <img
            src={restaurant.image_url}
            alt={restaurant.name}
            onError={() => setImageError(true)}
            className="h-full w-full object-cover transition-all duration-500 grayscale group-hover:grayscale-0 group-hover:scale-[1.02]"
          />
        )}
        {/* Delivery Time Badge */}
        {restaurant.delivery_time != null && (
          <div className="absolute right-3 bottom-3 rounded-none border border-border-default bg-surface px-2.5 py-1 text-xs font-medium text-text-primary">
            {restaurant.delivery_time} min
          </div>
        )}
      </div>

      <div className="p-5">
        <div className="mb-2 flex items-start justify-between gap-2">
          <h3 className="truncate text-lg font-medium text-text-primary">{restaurant.name}</h3>
          <span className="shrink-0 text-sm font-medium text-text-primary">
            ★ {restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}
          </span>
        </div>

        <p className="mb-4 line-clamp-2 text-sm text-text-secondary font-serif italic">{restaurant.description}</p>

        <div className="flex flex-wrap gap-2">
          {restaurant.cuisine_name ? (
            <span className="text-xs uppercase tracking-widest text-text-muted">
              {restaurant.cuisine_name}
            </span>
          ) : null}
        </div>
      </div>
    </Link>
  );
};

export default RestaurantCard;
