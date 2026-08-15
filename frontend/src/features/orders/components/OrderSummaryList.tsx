import type { FC } from 'react';
import { formatPrice } from '../../../utils/currency';

export interface SummaryItem {
  id: string | number;
  name: string;
  quantity: number;
  price: string | number;
}

interface OrderSummaryListProps {
  items: SummaryItem[];
  maxDisplay?: number;
}

const OrderSummaryList: FC<OrderSummaryListProps> = ({ items, maxDisplay }) => {
  const displayItems = maxDisplay ? items.slice(0, maxDisplay) : items;
  const remainingCount = items.length - displayItems.length;

  if (items.length === 0) return null;

  return (
    <div className="w-full">
      <ul className="space-y-4">
        {displayItems.map((item) => (
          <li key={item.id} className="flex justify-between items-start gap-4">
            <div className="flex-1 pr-4">
              <p className="text-xl font-serif italic text-text-primary line-clamp-2">
                <span className="font-sans font-bold text-text-primary mr-3 not-italic text-base">{item.quantity}x</span>
                {item.name}
              </p>
            </div>
            <p className="text-xl font-serif italic text-text-primary whitespace-nowrap">
              {formatPrice(item.price)}
            </p>
          </li>
        ))}
      </ul>
      {remainingCount > 0 && (
        <p className="mt-4 text-xs tracking-widest uppercase text-text-muted">
          + {remainingCount} more item{remainingCount !== 1 ? 's' : ''}...
        </p>
      )}
    </div>
  );
};

export default OrderSummaryList;
