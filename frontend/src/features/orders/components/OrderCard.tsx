import type { FC } from 'react';
import type { Order } from '../types/order.types';
import OrderStatusBadge from './OrderStatusBadge';

interface OrderCardProps {
    order: Order;
}

const formatOrderDate = (dateValue: string): string => {
    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return dateValue;
    }

    return new Intl.DateTimeFormat(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
    }).format(date);
};

const OrderCard: FC<OrderCardProps> = ({ order }) => {
    const itemLabel = order.itemCount === 1 ? 'item' : 'items';

    return (
        <article className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-500">Order #{order.id}</p>
                    <h2 className="mt-1 text-xl font-bold text-gray-900">
                        {order.restaurantName ?? 'Restaurant unavailable'}
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">{formatOrderDate(order.createdAt)}</p>
                </div>
                <OrderStatusBadge status={order.status} />
            </div>

            <div className="my-5 border-y border-gray-100 py-4">
                <div className="mb-3 flex items-center justify-between gap-4">
                    <h3 className="font-semibold text-gray-900">Order summary</h3>
                    <span className="text-sm text-gray-500">{order.itemCount} {itemLabel}</span>
                </div>
                <ul className="space-y-2 text-sm text-gray-600">
                    {order.items.map((item) => (
                        <li key={item.id} className="flex items-start justify-between gap-4">
                            <span>{item.name}</span>
                            <span className="shrink-0 font-medium text-gray-700">× {item.quantity}</span>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="flex items-center justify-between gap-4">
                <span className="font-medium text-gray-600">Total</span>
                <span className="text-lg font-bold text-gray-900">{order.totalPrice}</span>
            </div>
        </article>
    );
};

export default OrderCard;