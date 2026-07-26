import type { FC } from 'react';
import type { MenuCategory } from '../types/restaurant.types';

export interface CategoryNavbarProps {
  categories: MenuCategory[];
}

const CategoryNavbar: FC<CategoryNavbarProps> = ({ categories }) => {
  if (categories.length === 0) return null;

  return (
    <nav aria-label="Menu categories" className="flex gap-2 overflow-x-auto pb-1">
      {categories.map((category) => (
        <a
          key={category.id}
          href={`#category-${category.id}`}
          className="whitespace-nowrap rounded-full bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 transition-colors hover:bg-[#0B132B] hover:text-white"
        >
          {category.name}
        </a>
      ))}
    </nav>
  );
};

export default CategoryNavbar;
