import type { FC } from 'react';
import type { OrderStatus } from '../types/order.types';
import { Badge, type BadgeVariant } from '../../../components/common';

interface OrderStatusBadgeProps {
    status: OrderStatus;
}

const statusVariants: Record<OrderStatus, BadgeVariant> = {
    Pending: 'warning',
    Preparing: 'warning',
    Ready: 'info',
    Delivering: 'info',
    Completed: 'success',
    Cancelled: 'error',
};

const OrderStatusBadge: FC<OrderStatusBadgeProps> = ({ status }) => (
    <Badge variant={statusVariants[status] || 'secondary'} size="sm">
        {status}
    </Badge>
);

export default OrderStatusBadge;