import { useState, type FC } from 'react';
import { Link } from 'react-router-dom';
import type { Restaurant } from '../types/restaurant.types';
import { Badge } from '../../../components/common';

interface RestaurantCardProps {
  restaurant: Restaurant;
}

const RestaurantCard: FC<RestaurantCardProps> = ({ restaurant }) => {
  const [imageError, setImageError] = useState(false);
  const showPlaceholder = !restaurant.image_url || imageError;

  return (
    <Link
      to={`/restaurants/${restaurant.id}`}
      className="group block overflow-hidden rounded-xl border border-border-default bg-card shadow-subtle transition-all duration-300 hover:border-border-focus hover:shadow-elevated focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
      aria-label={`View ${restaurant.name} menu`}
    >
      {/* Image container with fixed aspect ratio */}
      <div className="relative h-48 w-full overflow-hidden bg-primary">
        {showPlaceholder ? (
          <div className="flex h-full w-full flex-col items-center justify-center bg-gradient-to-br from-primary via-primary-hover to-accent/80 p-4 text-center transition-transform duration-500 group-hover:scale-105">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-full border border-white/15 bg-white/10 text-2xl shadow-inner backdrop-blur-md">
              🍽️
            </div>
            <span className="max-w-full truncate px-2 text-sm font-bold tracking-wide text-white opacity-90">
              {restaurant.name}
            </span>
          </div>
        ) : (
          <img
            src={restaurant.image_url}
            alt={restaurant.name}
            onError={() => setImageError(true)}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        )}
        {/* Delivery Time Badge */}
        {restaurant.delivery_time != null && (
          <div className="absolute right-3 bottom-3 rounded-full border border-border-default bg-surface/95 px-2.5 py-1 text-xs font-bold text-text-primary shadow-md backdrop-blur-sm">
            {restaurant.delivery_time} min
          </div>
        )}
      </div>

      <div className="p-5">
        <div className="mb-1.5 flex items-start justify-between gap-2">
          <h3 className="truncate text-lg font-bold text-text-primary">{restaurant.name}</h3>
          <Badge variant="secondary" size="sm" className="shrink-0 bg-secondary font-semibold text-text-primary">
            <span className="text-accent">★</span>
            <span>{restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}</span>
          </Badge>
        </div>

        <p className="mb-3 line-clamp-2 text-sm text-text-secondary">{restaurant.description}</p>

        <div className="flex flex-wrap gap-2">
          {restaurant.cuisine_name ? (
            <Badge variant="neutral" size="sm">
              {restaurant.cuisine_name}
            </Badge>
          ) : null}
        </div>
      </div>
    </Link>
  );
};

export default RestaurantCard;
