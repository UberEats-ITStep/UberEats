import type { FC } from 'react';
import type { MenuItem } from '../types/restaurant.types';

interface MenuItemCardProps {
  item: MenuItem;
}

const formatPrice = (price: string) => {
  const numericPrice = Number(price);
  return Number.isFinite(numericPrice)
    ? new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(numericPrice)
    : price;
};

const MenuItemCard: FC<MenuItemCardProps> = ({ item }) => (
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
      {!item.is_available && (
        <p className="mt-auto pt-3 text-sm font-semibold text-orange-700">
          {item.unavailable_reason || 'Currently unavailable'}
        </p>
      )}
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
