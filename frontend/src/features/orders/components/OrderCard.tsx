import type { FC } from 'react';
import type { Order } from '../types/order.types';
import OrderStatusBadge from './OrderStatusBadge';
import { Card } from '../../../components/common';

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
        <Card elevation="subtle" padding="md">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                    <p className="text-caption">Order #{order.id}</p>
                    <h2 className="mt-1 text-xl font-bold text-text-primary">
                        {order.restaurantName ?? 'Restaurant unavailable'}
                    </h2>
                    <p className="mt-1 text-xs text-text-muted">{formatOrderDate(order.createdAt)}</p>
                </div>
                <OrderStatusBadge status={order.status} />
            </div>

            <div className="my-5 border-y border-border-default py-4">
                <div className="mb-3 flex items-center justify-between gap-4">
                    <h3 className="font-semibold text-text-primary">Order summary</h3>
                    <span className="text-xs text-text-muted">{order.itemCount} {itemLabel}</span>
                </div>
                <ul className="space-y-2 text-sm text-text-secondary">
                    {order.items.map((item) => (
                        <li key={item.id} className="flex items-start justify-between gap-4">
                            <span>{item.name}</span>
                            <span className="shrink-0 font-medium text-text-primary">× {item.quantity}</span>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="flex items-center justify-between gap-4">
                <span className="font-semibold text-text-secondary">Total</span>
                <span className="text-lg font-bold text-text-primary">{order.totalPrice}</span>
            </div>
        </Card>
    );
};

export default OrderCard;