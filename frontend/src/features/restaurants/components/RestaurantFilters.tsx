import type { FC } from 'react';
import { Select } from '../../../components/common';
import type { Cuisine, RestaurantOrdering } from '../types/restaurant.types';

export interface RestaurantFilterValues {
  cuisine: string;
  minRating: string;
  ordering: RestaurantOrdering;
}

interface RestaurantFiltersProps {
  values: RestaurantFilterValues;
  cuisines: Cuisine[];
  onChange: (values: RestaurantFilterValues) => void;
  onClear: () => void;
}

const RestaurantFilters: FC<RestaurantFiltersProps> = ({ values, cuisines, onChange, onClear }) => {
  const update = (field: keyof RestaurantFilterValues) => (value: string) => {
    onChange({ ...values, [field]: value });
  };
  const hasFilters = Object.values(values).some(Boolean);

  return (
    <section aria-label="Restaurant filters" className="flex flex-wrap items-center gap-3">
      <Select
        value={values.cuisine}
        onChange={update('cuisine')}
        options={[
          { label: 'Any cuisine', value: '' },
          ...cuisines.map((c) => ({ label: c.name, value: String(c.id) })),
        ]}
        placeholder="Any cuisine"
        aria-label="Filter by cuisine"
      />

      <Select
        value={values.minRating}
        onChange={update('minRating')}
        options={[
          { label: 'Any rating', value: '' },
          { label: '4.0+ Stars', value: '4' },
          { label: '3.0+ Stars', value: '3' },
          { label: '2.0+ Stars', value: '2' },
        ]}
        placeholder="Any rating"
        aria-label="Filter by minimum rating"
      />

      <Select
        value={values.ordering}
        onChange={update('ordering')}
        options={[
          { label: 'Recommended', value: '' },
          { label: 'Highest rated', value: '-rating' },
          { label: 'Fastest delivery', value: 'delivery_time' },
          { label: 'Name A–Z', value: 'name' },
        ]}
        placeholder="Sort restaurants"
        aria-label="Sort restaurants"
      />

      {hasFilters && (
        <button 
          onClick={onClear} 
          className="ml-2 text-sm font-medium text-text-muted hover:text-text-primary transition-base underline underline-offset-4"
        >
          Clear
        </button>
      )}
    </section>
  );
};

export default RestaurantFilters;
