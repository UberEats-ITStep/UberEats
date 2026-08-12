import { useState } from 'react';
import type { FC, ReactNode } from 'react';
import type { MenuItem } from '../types/restaurant.types';
import { formatPrice } from '../../../utils/currency';

export interface MenuItemCardProps {
  item: MenuItem;
  onAddToCart?: (item: MenuItem) => void;
  actionSlot?: ReactNode;
}

const MenuItemCard: FC<MenuItemCardProps> = ({ item, onAddToCart, actionSlot }) => {
  const [imageError, setImageError] = useState(false);
  const showPlaceholder = !item.image || imageError;

  return (
    <article
      className={`flex min-h-44 overflow-hidden rounded-xl border bg-card shadow-subtle transition-card hover:border-border-focus hover:shadow-elevated ${
        item.is_available ? 'border-border-default' : 'border-border-default opacity-70'
      }`}
    >
      <div className="flex min-w-0 flex-1 flex-col p-5">
        <div className="mb-2 flex items-start justify-between gap-4">
          <h3 className="text-lg font-bold text-text-primary">{item.name}</h3>
          <span className="shrink-0 font-bold text-text-primary">
            {formatPrice(item.price)}
          </span>
        </div>
        <p className="line-clamp-3 text-sm leading-6 text-text-secondary">
          {item.description || 'A delicious choice from this restaurant.'}
        </p>
        
        <div className="mt-auto pt-3 flex items-center gap-3">
          {!item.is_available ? (
            <p className="text-sm font-semibold text-status-warning">
              {item.unavailable_reason || 'Currently unavailable'}
            </p>
          ) : (
            <>
              {actionSlot}
              {onAddToCart && (
                <button
                  type="button"
                  aria-label="Add to cart"
                  className="mt-2 flex h-8 w-8 items-center justify-center rounded-full bg-surface border border-border-default text-xl font-medium text-text-primary shadow-subtle transition-colors hover:bg-surface-hover hover:border-border-focus focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  onClick={() => onAddToCart(item)}
                >
                  +
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <div className="w-36 shrink-0 bg-secondary sm:w-44">
        {showPlaceholder ? (
          <div className="flex h-full w-full flex-col items-center justify-center bg-gradient-to-br from-secondary via-secondary/80 to-surface/40 p-4 text-center">
            <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-full border border-border-default bg-surface/50 text-xl shadow-inner backdrop-blur-sm">
              🍲
            </div>
          </div>
        ) : (
          <img
            src={item.image!}
            alt={item.name}
            onError={() => setImageError(true)}
            className="h-full w-full object-cover"
            loading="lazy"
          />
        )}
      </div>
    </article>
  );
};

export default MenuItemCard;
