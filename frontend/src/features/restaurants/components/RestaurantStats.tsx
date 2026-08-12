import type { FC } from 'react';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface RestaurantStatsProps {
  restaurant: RestaurantDetails;
}

const RestaurantStats: FC<RestaurantStatsProps> = ({ restaurant }) => (
  <section
    aria-label="Restaurant information"
    className="relative z-10 mx-4 -mt-5 grid gap-4 rounded-xl border border-border-default bg-card p-5 shadow-elevated sm:grid-cols-2 lg:mx-8 lg:grid-cols-4"
  >
    <div>
      <p className="text-caption">Rating</p>
      <p className="mt-1 font-bold text-text-primary">
        <span className="text-accent">★</span>{' '}
        {restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}
        {restaurant.review_count > 0 && (
          <span className="ml-1 font-normal text-text-muted">
            ({restaurant.review_count})
          </span>
        )}
      </p>
    </div>
    <div>
      <p className="text-caption">Delivery</p>
      <p className="mt-1 font-bold text-text-primary">
        {restaurant.delivery_time != null
          ? `${restaurant.delivery_time} min`
          : 'Time unavailable'}
      </p>
    </div>
    <div className="sm:col-span-2">
      <p className="text-caption">Address</p>
      <p className="mt-1 font-bold text-text-primary">
        {restaurant.address || 'Address unavailable'}
      </p>
    </div>
  </section>
);

export default RestaurantStats;
