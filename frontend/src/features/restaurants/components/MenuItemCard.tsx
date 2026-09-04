import { useState } from 'react';
import type { FC, ReactNode } from 'react';
import type { MenuItem } from '../types/restaurant.types';
import { formatPrice } from '../../../utils/currency';

export interface MenuItemCardProps {
  item: MenuItem;
  onAddToCart?: (item: MenuItem) => void;
  actionSlot?: ReactNode;
  isLoading?: boolean;
  isHighlighted?: boolean;
}

const MenuItemCard: FC<MenuItemCardProps> = ({ item, onAddToCart, actionSlot, isLoading, isHighlighted }) => {
  const [imageError, setImageError] = useState(false);
  const showPlaceholder = !item.image || imageError;

  return (
    <article
      id={`item-${item.id}`}
      className={`group flex items-start gap-6 p-5 sm:p-6 bg-surface border transition-all hover:border-border-focus hover:shadow-subtle ${
        isHighlighted ? 'border-primary ring-1 ring-primary shadow-subtle animate-fade-in' : 'border-border-default'
      } ${!item.is_available ? 'opacity-60' : ''}`}
    >
      <div className="flex-1 min-w-0 flex flex-col justify-between self-stretch">
        <div>
          <div className="flex items-baseline justify-between gap-4 mb-1">
            <h3 className="text-xl font-medium text-text-primary group-hover:text-primary-hover transition-colors">
              {item.name}
            </h3>
            <span className="shrink-0 font-serif italic text-lg text-text-primary font-bold">
              {formatPrice(item.price)}
            </span>
          </div>
          <p className="line-clamp-2 text-sm text-text-secondary pr-8">
            {item.description || 'A curated choice from this restaurant.'}
          </p>
        </div>
        
        <div className="mt-4 flex items-center gap-3">
          {!item.is_available ? (
            <span className="text-[10px] uppercase tracking-widest text-status-warning font-bold">
              {item.unavailable_reason || 'Unavailable'}
            </span>
          ) : (
            <>
              {actionSlot}
              {onAddToCart && (
                <button
                  type="button"
                  aria-label="Add to cart"
                  disabled={isLoading}
                  className="px-4 py-1.5 bg-primary text-surface text-[10px] uppercase font-bold tracking-widest transition-colors hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() => onAddToCart(item)}
                >
                  Add
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <div className="w-24 h-24 md:w-32 md:h-32 shrink-0 bg-secondary overflow-hidden">
        {!showPlaceholder && (
          <img
            src={item.image!}
            alt={item.name}
            onError={() => setImageError(true)}
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
            loading="lazy"
          />
        )}
      </div>
    </article>
  );
};

export default MenuItemCard;
