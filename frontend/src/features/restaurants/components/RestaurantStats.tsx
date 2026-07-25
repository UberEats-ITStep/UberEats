import type { FC } from 'react';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface RestaurantStatsProps {
  restaurant: RestaurantDetails;
}

const RestaurantStats: FC<RestaurantStatsProps> = ({ restaurant }) => (
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
);

export default RestaurantStats;
