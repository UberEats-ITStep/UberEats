import type { FC } from 'react';
import type { MenuCategory } from '../types/restaurant.types';

export interface CategoryNavbarProps {
  categories: MenuCategory[];
}

const CategoryNavbar: FC<CategoryNavbarProps> = ({ categories }) => {
  if (categories.length === 0) return null;

  return (
    <nav aria-label="Menu categories" className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide lg:justify-end">
      {categories.map((category) => (
        <a
          key={category.id}
          href={`#category-${category.id}`}
          className="whitespace-nowrap border-b-2 border-transparent px-1 py-2 text-sm font-medium tracking-wide text-text-secondary transition-base hover:border-text-primary hover:text-text-primary"
        >
          {category.name}
        </a>
      ))}
    </nav>
  );
};

export default CategoryNavbar;
