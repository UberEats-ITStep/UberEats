import type { FC } from 'react';
import type { RestaurantDetails } from '../types/restaurant.types';

export interface RestaurantStatsProps {
  restaurant: RestaurantDetails;
}

const RestaurantStats: FC<RestaurantStatsProps> = ({ restaurant }) => (
  <section
    aria-label="Restaurant information"
    className="relative z-10 grid gap-6 border-b border-border-default bg-surface py-6 px-6 sm:px-12 sm:grid-cols-3"
  >
    <div>
      <p className="text-xs tracking-widest uppercase text-text-muted mb-2">Rating</p>
      <p className="text-2xl font-serif italic text-text-primary">
        ★ {restaurant.rating != null ? Number(restaurant.rating).toFixed(1) : 'New'}
        {restaurant.review_count > 0 && (
          <span className="ml-2 text-lg font-sans not-italic text-text-muted">
            ({restaurant.review_count})
          </span>
        )}
      </p>
    </div>
    <div>
      <p className="text-xs tracking-widest uppercase text-text-muted mb-2">Delivery</p>
      <p className="text-2xl font-serif italic text-text-primary">
        {restaurant.delivery_time != null
          ? `${restaurant.delivery_time} min`
          : 'Time unavailable'}
      </p>
    </div>
    <div>
      <p className="text-xs tracking-widest uppercase text-text-muted mb-2">Address</p>
      <p className="text-2xl font-serif italic text-text-primary">
        {restaurant.address || 'Address unavailable'}
      </p>
    </div>
  </section>
);

export default RestaurantStats;
