import type { FC, ReactNode } from 'react';
import type { MenuItem } from '../types/restaurant.types';
import { formatPrice } from '../../../utils/currency';
import { Button } from '../../../components/common';

export interface MenuItemCardProps {
  item: MenuItem;
  onAddToCart?: (item: MenuItem) => void;
  actionSlot?: ReactNode;
}

const MenuItemCard: FC<MenuItemCardProps> = ({ item, onAddToCart, actionSlot }) => (
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
      
      <div className="mt-auto pt-3 flex items-center justify-between gap-3">
        {!item.is_available ? (
          <p className="text-sm font-semibold text-status-warning">
            {item.unavailable_reason || 'Currently unavailable'}
          </p>
        ) : (
          <>
            {actionSlot}
            {onAddToCart && (
              <Button
                type="button"
                variant="accent"
                size="sm"
                onClick={() => onAddToCart(item)}
              >
                Add to cart
              </Button>
            )}
          </>
        )}
      </div>
    </div>

    {item.image && (
      <div className="w-36 shrink-0 bg-secondary sm:w-44">
        <img
          src={item.image}
          alt={item.name}
          className="h-full w-full object-cover"
          loading="lazy"
        />
      </div>
    )}
  </article>
);

export default MenuItemCard;
