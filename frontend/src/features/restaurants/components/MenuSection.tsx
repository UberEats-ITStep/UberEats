import type { FC } from 'react';
import { useLocation } from 'react-router-dom';
import type { MenuCategory, MenuItem } from '../types/restaurant.types';
import MenuItemCard from './MenuItemCard';
import { EmptyState } from '../../../components/common';
import { useEffect } from 'react';

export interface MenuSectionProps {
  categories: MenuCategory[];
  onAddToCart?: (item: MenuItem) => void;
  isLoading?: boolean;
}

const MenuSection: FC<MenuSectionProps> = ({ categories, onAddToCart, isLoading }) => {
  const location = useLocation();
  const highlightedItemId = location.hash ? location.hash.replace('#item-', '') : null;

  useEffect(() => {
    if (location.hash) {
      // Small delay to ensure render is complete before scrolling
      setTimeout(() => {
        const element = document.getElementById(location.hash.substring(1));
        if (element) {
          // Scroll with a small offset for the sticky header
          const y = element.getBoundingClientRect().top + window.scrollY - 100;
          window.scrollTo({ top: y, behavior: 'smooth' });
        }
      }, 100);
    }
  }, [location.hash, categories]);

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
          <div className="mb-6 border-b-2 border-primary pb-4 flex items-baseline justify-between gap-4">
            <h2 className="text-3xl font-serif italic text-text-primary">
              {category.name}
            </h2>
            <span className="text-[10px] tracking-widest uppercase font-bold text-text-muted">
              {category.menu_items.length}{' '}
              {category.menu_items.length === 1 ? 'item' : 'items'}
            </span>
          </div>

          {category.menu_items.length === 0 ? (
            <div className="py-8 text-text-secondary text-sm italic">
              Nothing is available in {category.name} right now.
            </div>
          ) : (
            <div className="grid gap-6 lg:grid-cols-2">
              {category.menu_items.map((item) => (
                <MenuItemCard 
                  key={item.id} 
                  item={item} 
                  onAddToCart={onAddToCart} 
                  isLoading={isLoading}
                  isHighlighted={highlightedItemId === item.id.toString()}
                />
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
};

export default MenuSection;
