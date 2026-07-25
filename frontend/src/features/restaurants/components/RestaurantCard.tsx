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
      className="block bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden border border-gray-100 group focus:outline-none focus:ring-2 focus:ring-[#FF8C00] focus:ring-offset-2"
      aria-label={`View ${restaurant.name} menu`}
    >
      {/* Image container with fixed aspect ratio */}
      <div className="relative h-48 w-full overflow-hidden bg-[#0B132B]">
        {showPlaceholder ? (
          <div className="w-full h-full bg-gradient-to-br from-[#0B132B] via-[#172344] to-[#FF8C00]/80 flex flex-col items-center justify-center p-4 text-center group-hover:scale-105 transition-transform duration-500">
            <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center mb-2 text-2xl shadow-inner border border-white/15">
              🍽️
            </div>
            <span className="text-white font-bold text-sm tracking-wide opacity-90 truncate max-w-full px-2">
              {restaurant.name}
            </span>
          </div>
        ) : (
          <img
            src={restaurant.image_url}
            alt={restaurant.name}
            onError={() => setImageError(true)}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        )}
        {/* Delivery Time Badge */}
        {restaurant.delivery_time != null && (
          <div className="absolute bottom-3 right-3 bg-white/95 backdrop-blur-sm px-2.5 py-1 rounded-full text-xs font-bold text-[#0B132B] shadow-md border border-gray-100">
            {restaurant.delivery_time} min
          </div>
        )}
      </div>

      <div className="p-4">
        <div className="flex justify-between items-start mb-1">
          <h3 className="text-lg font-bold text-gray-900 truncate pr-2">{restaurant.name}</h3>
          <div className="flex items-center bg-gray-100 px-2 py-1 rounded-full shrink-0">
            <span className="text-[#FF8C00] mr-1 text-sm">★</span>
            <span className="text-sm font-semibold text-[#0B132B]">
              {restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}
            </span>
          </div>
        </div>

        <p className="text-sm text-gray-500 mb-3 line-clamp-2">{restaurant.description}</p>

        <div className="flex flex-wrap gap-2">
          {restaurant.cuisine_name ? (
            <span className="inline-block px-2 py-1 bg-gray-50 text-gray-600 text-xs font-medium rounded border border-gray-200">
              {restaurant.cuisine_name}
            </span>
          ) : null}
        </div>
      </div>
    </Link>
  );
};

export default RestaurantCard;
