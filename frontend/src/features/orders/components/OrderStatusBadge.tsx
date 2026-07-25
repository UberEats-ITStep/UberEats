import type { FC } from 'react';
import type { OrderStatus } from '../types/order.types';

interface OrderStatusBadgeProps {
    status: OrderStatus;
}

const statusClasses: Record<OrderStatus, string> = {
    Pending: 'bg-amber-100 text-amber-800',
    Preparing: 'bg-yellow-100 text-yellow-800',
    Ready: 'bg-blue-100 text-blue-800',
    Delivering: 'bg-violet-100 text-violet-800',
    Completed: 'bg-green-100 text-green-800',
    Cancelled: 'bg-red-100 text-red-800',
};

const OrderStatusBadge: FC<OrderStatusBadgeProps> = ({ status }) => (
    <span className={`inline-flex shrink-0 rounded-full px-3 py-1 text-sm font-medium ${statusClasses[status]}`}>
        {status}
    </span>
);

export default OrderStatusBadge;