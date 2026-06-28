import type { FC } from 'react';
import type { Restaurant } from '../types/restaurant.types';

interface RestaurantCardProps {
  restaurant: Restaurant;
}

const RestaurantCard: FC<RestaurantCardProps> = ({ restaurant }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden border border-gray-100 group cursor-pointer">
      {/* Image container with fixed aspect ratio */}
      <div className="relative h-48 w-full overflow-hidden bg-gray-200">
        <img
          src={restaurant.image}
          alt={restaurant.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
        {/* Delivery Time Badge */}
        <div className="absolute bottom-3 right-3 bg-white px-2 py-1 rounded-full text-xs font-semibold text-gray-800 shadow-sm">
          {restaurant.deliveryTime}
        </div>
      </div>

      <div className="p-4">
        <div className="flex justify-between items-start mb-1">
          <h3 className="text-lg font-bold text-gray-900 truncate pr-2">{restaurant.name}</h3>
          <div className="flex items-center bg-gray-100 px-2 py-1 rounded-full shrink-0">
            <span className="text-yellow-500 mr-1 text-sm">★</span>
            <span className="text-sm font-semibold text-gray-800">{restaurant.rating.toFixed(1)}</span>
          </div>
        </div>

        <p className="text-sm text-gray-500 mb-3 line-clamp-2">{restaurant.description}</p>

        <div className="flex flex-wrap gap-2">
          {restaurant.categories.map((category) => (
            <span
              key={category}
              className="inline-block px-2 py-1 bg-gray-50 text-gray-600 text-xs font-medium rounded border border-gray-200"
            >
              {category}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RestaurantCard;
