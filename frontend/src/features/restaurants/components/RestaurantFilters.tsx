import type { ChangeEvent, FC } from 'react';
import Input from '../../../components/common/Input';
import Button from '../../../components/common/Button';
import type { Cuisine, RestaurantOrdering } from '../types/restaurant.types';

export interface RestaurantFilterValues {
  search: string;
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

const selectClasses = 'w-full rounded-sm border border-border-default bg-surface px-3.5 py-2.5 text-sm text-text-primary transition-base focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1';

const RestaurantFilters: FC<RestaurantFiltersProps> = ({ values, cuisines, onChange, onClear }) => {
  const update = (field: keyof RestaurantFilterValues) => (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    onChange({ ...values, [field]: event.target.value });
  };
  const hasFilters = Object.values(values).some(Boolean);

  return (
    <section aria-label="Restaurant search and filters" className="mb-8 rounded-xl border border-border-default bg-surface p-4 shadow-subtle sm:p-5">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-[minmax(16rem,2fr)_1fr_1fr_1fr_auto] lg:items-end">
        <label className="block md:col-span-2 lg:col-span-1">
          <span className="mb-1.5 block text-label">Search</span>
          <Input type="search" value={values.search} onChange={update('search')} placeholder="Restaurant, cuisine, or menu item" aria-label="Search restaurants and menu items" />
        </label>
        <label className="block">
          <span className="mb-1.5 block text-label">Cuisine</span>
          <select className={selectClasses} value={values.cuisine} onChange={update('cuisine')}>
            <option value="">All cuisines</option>
            {cuisines.map((cuisine) => <option key={cuisine.id} value={cuisine.id}>{cuisine.name}</option>)}
          </select>
        </label>
        <label className="block">
          <span className="mb-1.5 block text-label">Minimum rating</span>
          <select className={selectClasses} value={values.minRating} onChange={update('minRating')}>
            <option value="">Any rating</option>
            <option value="4">4.0+</option>
            <option value="3">3.0+</option>
            <option value="2">2.0+</option>
          </select>
        </label>
        <label className="block">
          <span className="mb-1.5 block text-label">Sort by</span>
          <select className={selectClasses} value={values.ordering} onChange={update('ordering')}>
            <option value="">Recommended</option>
            <option value="-rating">Highest rated</option>
            <option value="delivery_time">Fastest delivery</option>
            <option value="name">Name A–Z</option>
          </select>
        </label>
        <Button variant="outline" onClick={onClear} disabled={!hasFilters} className="w-full lg:w-auto">Clear</Button>
      </div>
    </section>
  );
};

export default RestaurantFilters;
