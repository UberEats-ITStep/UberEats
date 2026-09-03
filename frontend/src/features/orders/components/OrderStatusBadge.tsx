import type { FC } from 'react';
import type { OrderStatus } from '../types/order.types';
import { Badge, type BadgeVariant } from '../../../components/common';

interface OrderStatusBadgeProps {
    status: OrderStatus;
}

const statusVariants: Record<OrderStatus, BadgeVariant> = {
    PENDING: 'warning',
    ACCEPTED: 'warning',
    PREPARING: 'warning',
    READY: 'info',
    DELIVERING: 'info',
    COMPLETED: 'success',
    CANCELLED: 'error',
};

const OrderStatusBadge: FC<OrderStatusBadgeProps> = ({ status }) => (
    <Badge variant={statusVariants[status] || 'secondary'} size="sm">
        {status}
    </Badge>
);

export default OrderStatusBadge;