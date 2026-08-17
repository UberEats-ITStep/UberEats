import type { FC } from 'react';
import { formatPrice } from '../../../utils/currency';
import type { OrderItem } from '../types/order.types';

interface OrderItemsListProps {
  items: OrderItem[];
}

const OrderItemsList: FC<OrderItemsListProps> = ({ items }) => {
  if (items.length === 0) {
    return <p className="py-6 text-text-secondary">No item details are available for this order.</p>;
  }

  return (
    <ul className="divide-y divide-border-default">
      {items.map((item) => {
        const subtotal = item.subtotal ?? Number(item.price) * item.quantity;
        return (
          <li key={item.id} className="grid gap-3 py-5 sm:grid-cols-[1fr_auto_auto] sm:items-center sm:gap-8">
            <div>
              <p className="text-lg font-bold text-text-primary">
                {item.menu_item_name ?? `Item #${item.menu_item}`}
              </p>
              <p className="mt-1 text-sm text-text-muted">{formatPrice(item.price)} each</p>
            </div>
            <p className="text-sm text-text-secondary sm:text-right">Quantity: {item.quantity}</p>
            <p className="font-serif text-xl italic text-text-primary sm:min-w-24 sm:text-right">
              {formatPrice(subtotal)}
            </p>
          </li>
        );
      })}
    </ul>
  );
};

export default OrderItemsList;
