import type { FC, ReactNode } from 'react';
import type { MenuItem } from '../types/restaurant.types';
import { formatPrice } from '../../../utils/currency';

export interface MenuItemCardProps {
  item: MenuItem;
  onAddToCart?: (item: MenuItem) => void;
  actionSlot?: ReactNode;
}

const MenuItemCard: FC<MenuItemCardProps> = ({ item, onAddToCart, actionSlot }) => (
  <article
    className={`flex min-h-44 overflow-hidden rounded-2xl border bg-white shadow-sm transition-shadow hover:shadow-md ${
      item.is_available ? 'border-gray-200' : 'border-gray-200 opacity-70'
    }`}
  >
    <div className="flex min-w-0 flex-1 flex-col p-5">
      <div className="mb-2 flex items-start justify-between gap-4">
        <h3 className="text-lg font-bold text-[#0B132B]">{item.name}</h3>
        <span className="shrink-0 font-bold text-[#0B132B]">
          {formatPrice(item.price)}
        </span>
      </div>
      <p className="line-clamp-3 text-sm leading-6 text-gray-600">
        {item.description || 'A delicious choice from this restaurant.'}
      </p>
      
      <div className="mt-auto pt-3 flex items-center justify-between gap-3">
        {!item.is_available ? (
          <p className="text-sm font-semibold text-orange-700">
            {item.unavailable_reason || 'Currently unavailable'}
          </p>
        ) : (
          <>
            {actionSlot}
            {onAddToCart && (
              <button
                type="button"
                onClick={() => onAddToCart(item)}
                className="rounded-lg bg-[#FF8C00] px-3 py-1.5 text-xs font-bold text-[#0B132B] transition-colors hover:bg-[#e07b00]"
              >
                Add to cart
              </button>
            )}
          </>
        )}
      </div>
    </div>

    {item.image && (
      <div className="w-36 shrink-0 bg-gray-100 sm:w-44">
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
