import { useState } from 'react';
import type { FC, ReactNode } from 'react';
import type { MenuItem } from '../types/restaurant.types';
import { formatPrice } from '../../../utils/currency';

export interface MenuItemCardProps {
  item: MenuItem;
  onAddToCart?: (item: MenuItem) => void;
  actionSlot?: ReactNode;
  isLoading?: boolean;
}

const MenuItemCard: FC<MenuItemCardProps> = ({ item, onAddToCart, actionSlot, isLoading }) => {
  const [imageError, setImageError] = useState(false);
  const showPlaceholder = !item.image || imageError;

  return (
    <article
      className={`group flex min-h-44 overflow-hidden rounded-none border bg-card transition-all duration-300 hover:border-border-focus ${
        item.is_available ? 'border-border-default' : 'border-border-default opacity-60'
      }`}
    >
      <div className="flex min-w-0 flex-1 flex-col p-6">
        <div className="mb-3 flex items-start justify-between gap-4">
          <h3 className="text-xl font-bold text-text-primary leading-tight">{item.name}</h3>
          <span className="shrink-0 font-medium text-text-primary">
            {formatPrice(item.price)}
          </span>
        </div>
        <p className="line-clamp-3 text-sm leading-relaxed text-text-secondary font-serif italic">
          {item.description || 'A curated choice from this restaurant.'}
        </p>
        
        <div className="mt-auto pt-4 flex items-center gap-3">
          {!item.is_available ? (
            <p className="text-xs uppercase tracking-widest text-status-warning font-medium">
              {item.unavailable_reason || 'Unavailable'}
            </p>
          ) : (
            <>
              {actionSlot}
              {onAddToCart && (
                <button
                  type="button"
                  aria-label="Add to cart"
                  disabled={isLoading}
                  className="mt-2 flex h-8 w-8 items-center justify-center rounded-none bg-primary text-xl font-medium text-surface transition-all duration-300 hover:bg-secondary hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed"
                  onClick={() => onAddToCart(item)}
                >
                  +
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <div className="w-36 shrink-0 border-l border-border-default bg-muted sm:w-44">
        {showPlaceholder ? (
          <div className="flex h-full w-full flex-col items-center justify-center bg-primary p-4 text-center">
            <span className="text-surface font-serif italic tracking-wide opacity-50">
              BiteUp.
            </span>
          </div>
        ) : (
          <img
            src={item.image!}
            alt={item.name}
            onError={() => setImageError(true)}
            className="h-full w-full object-cover grayscale transition-all duration-500 group-hover:grayscale-0 group-hover:scale-105"
            loading="lazy"
          />
        )}
      </div>
    </article>
  );
};

export default MenuItemCard;
