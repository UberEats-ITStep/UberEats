import type { FC } from 'react';
import type { MenuCategory, MenuItem } from '../types/restaurant.types';
import MenuItemCard from './MenuItemCard';
import { EmptyState } from '../../../components/common';

export interface MenuSectionProps {
  categories: MenuCategory[];
  onAddToCart?: (item: MenuItem) => void;
  isLoading?: boolean;
}

const MenuSection: FC<MenuSectionProps> = ({ categories, onAddToCart, isLoading }) => {
  const menuItemCount = categories.reduce(
    (total, category) => total + category.menu_items.length,
    0,
  );

  if (menuItemCount === 0) {
    return (
      <div className="mt-8">
        <EmptyState
          title="The menu is being prepared"
          description="This restaurant has no menu items available yet. Please check back soon."
        />
      </div>
    );
  }

  return (
    <div className="space-y-16 pt-12">
      {categories.map((category) => (
        <section
          key={category.id}
          id={`category-${category.id}`}
          className="scroll-mt-24"
        >
          <div className="mb-8 border-b border-text-primary pb-4 flex items-baseline justify-between gap-4">
            <h2 className="text-3xl font-serif italic text-text-primary">
              {category.name}
            </h2>
            <span className="text-sm tracking-widest uppercase font-medium text-text-muted">
              {category.menu_items.length}{' '}
              {category.menu_items.length === 1 ? 'item' : 'items'}
            </span>
          </div>

          {category.menu_items.length === 0 ? (
            <div className="border border-border-default bg-surface p-8 text-center text-text-secondary font-serif italic">
              Nothing is available in {category.name} right now.
            </div>
          ) : (
            <div className="grid gap-6 lg:grid-cols-2">
              {category.menu_items.map((item) => (
                <MenuItemCard key={item.id} item={item} onAddToCart={onAddToCart} isLoading={isLoading} />
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
};

export default MenuSection;
