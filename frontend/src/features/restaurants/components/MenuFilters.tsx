import type { FC } from 'react';
import { Input, Select } from '../../../components/common';

export interface MenuFiltersProps {
  categories: Array<{ id: number; name: string }>;
  searchTerm: string;
  selectedCategory: number | 'all';
  showAvailableOnly: boolean;
  onSearchChange: (value: string) => void;
  onCategoryChange: (value: number | 'all') => void;
  onAvailabilityToggle: (value: boolean) => void;
  onClear: () => void;
}

const MenuFilters: FC<MenuFiltersProps> = ({
  categories,
  searchTerm,
  selectedCategory,
  showAvailableOnly,
  onSearchChange,
  onCategoryChange,
  onAvailabilityToggle,
  onClear,
}) => {
  const hasFilters = Boolean(searchTerm.trim()) || selectedCategory !== 'all' || showAvailableOnly;

  return (
    <div className="rounded-none border border-border-default bg-surface p-4 shadow-subtle">
      <div className="flex flex-col gap-4 md:flex-row md:items-end">
        <div className="flex-1">
          <label htmlFor="menu-search" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.2em] text-text-muted">
            Search menu
          </label>
          <Input
            id="menu-search"
            value={searchTerm}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search dishes or ingredients"
            aria-label="Search menu items"
          />
        </div>

        <div className="w-full md:w-56">
          <label htmlFor="menu-category" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.2em] text-text-muted">
            Category
          </label>
          <Select
            value={selectedCategory === 'all' ? 'all' : String(selectedCategory)}
            onChange={(value) => onCategoryChange(value === 'all' ? 'all' : Number(value))}
            options={[
              { label: 'All categories', value: 'all' },
              ...categories.map((category) => ({
                label: category.name,
                value: String(category.id),
              })),
            ]}
            placeholder="All categories"
            aria-label="Filter by menu category"
            className="w-full"
          />
        </div>
      </div>

      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <label className="inline-flex cursor-pointer items-center gap-3 text-sm font-medium text-text-secondary">
          <input
            type="checkbox"
            checked={showAvailableOnly}
            onChange={(event) => onAvailabilityToggle(event.target.checked)}
            className="h-4 w-4 accent-primary border-border-default rounded-none focus:ring-primary"
          />
          <span className={showAvailableOnly ? 'text-text-primary' : 'text-text-secondary'}>
            Show available items only
          </span>
        </label>

        {hasFilters && (
          <button
            type="button"
            onClick={onClear}
            className="text-sm font-medium text-text-muted underline underline-offset-4 transition-base hover:text-text-primary"
          >
            Clear filters
          </button>
        )}
      </div>
    </div>
  );
};

export default MenuFilters;
