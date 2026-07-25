import type { FC } from 'react';
import type { MenuCategory, MenuItem } from '../types/restaurant.types';
import MenuItemCard from './MenuItemCard';

export interface MenuSectionProps {
  categories: MenuCategory[];
  onAddToCart?: (item: MenuItem) => void;
}

const MenuSection: FC<MenuSectionProps> = ({ categories, onAddToCart }) => {
  const menuItemCount = categories.reduce(
    (total, category) => total + category.menu_items.length,
    0,
  );

  if (menuItemCount === 0) {
    return (
      <div className="mt-8 rounded-2xl bg-gray-50 px-6 py-16 text-center">
        <h2 className="text-xl font-bold text-[#0B132B]">The menu is being prepared</h2>
        <p className="mt-2 text-gray-600">
          This restaurant has no menu items available yet. Please check back soon.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-12 pt-9">
      {categories.map((category) => (
        <section
          key={category.id}
          id={`category-${category.id}`}
          className="scroll-mt-24"
        >
          <div className="mb-5 flex items-baseline justify-between gap-4">
            <h2 className="text-2xl font-extrabold text-[#0B132B]">
              {category.name}
            </h2>
            <span className="text-sm text-gray-500">
              {category.menu_items.length}{' '}
              {category.menu_items.length === 1 ? 'item' : 'items'}
            </span>
          </div>

          {category.menu_items.length === 0 ? (
            <div className="rounded-2xl bg-gray-50 px-5 py-8 text-gray-600">
              Nothing is available in {category.name} right now.
            </div>
          ) : (
            <div className="grid gap-5 lg:grid-cols-2">
              {category.menu_items.map((item) => (
                <MenuItemCard key={item.id} item={item} onAddToCart={onAddToCart} />
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
};

export default MenuSection;
