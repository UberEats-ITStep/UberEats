import { useState, type FC } from 'react';
import { Link } from 'react-router-dom';
import type { Restaurant } from '../types/restaurant.types';

interface RestaurantCardProps {
  restaurant: Restaurant;
  isFeatured?: boolean;
  compact?: boolean;
}

const RestaurantCard: FC<RestaurantCardProps> = ({ restaurant, isFeatured = false, compact = false }) => {
  const [imageError, setImageError] = useState(false);
  const showPlaceholder = !restaurant.image_url || imageError;

  return (
    <Link
      to={`/restaurants/${restaurant.id}`}
      className="group flex flex-col h-full bg-surface border border-border-default overflow-hidden transition-all duration-300 hover:border-border-focus focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
      aria-label={`View ${restaurant.name} menu`}
    >
      {/* Image container */}
      <div className={`relative w-full overflow-hidden bg-secondary border-b border-border-default ${isFeatured ? 'h-72 md:h-96' : compact ? 'h-40 md:h-48' : 'h-56'}`}>
        {showPlaceholder ? (
          <div className="flex h-full w-full flex-col items-center justify-center bg-primary p-4 text-center">
            <span className="text-surface font-serif italic tracking-wide opacity-50 text-xl">
              BiteUp.
            </span>
          </div>
        ) : (
          <img
            src={restaurant.image_url}
            alt={restaurant.name}
            onError={() => setImageError(true)}
            className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
          />
        )}
        {/* Delivery Time Badge */}
        {restaurant.delivery_time != null && (
          <div className="absolute right-0 top-0 bg-surface px-3 py-1.5 text-xs font-bold uppercase tracking-widest text-text-primary shadow-subtle border-b border-l border-border-default">
            {restaurant.delivery_time} min
          </div>
        )}
      </div>

      <div className={`flex flex-col flex-1 ${isFeatured ? 'p-6 lg:p-8' : 'p-4 md:p-5'}`}>
        <div className="mb-2 flex items-start justify-between gap-4">
          <h3 className={`font-medium text-text-primary truncate transition-colors group-hover:text-primary-hover ${isFeatured ? 'text-2xl lg:text-3xl font-serif' : 'text-lg'}`}>
            {restaurant.name}
          </h3>
          <span className="shrink-0 text-sm font-medium text-text-primary pt-1">
            ★ {restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}
          </span>
        </div>

        {!compact && (
          <p className={`text-text-secondary font-serif italic mb-4 ${isFeatured ? 'text-lg line-clamp-3 max-w-2xl' : 'text-sm line-clamp-2'}`}>
            {restaurant.description}
          </p>
        )}

        <div className={`mt-auto ${compact ? 'pt-2' : ''}`}>
          {restaurant.cuisine_name && (
            <span className="text-[10px] md:text-xs uppercase tracking-widest text-text-muted font-bold">
              {restaurant.cuisine_name}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default RestaurantCard;
