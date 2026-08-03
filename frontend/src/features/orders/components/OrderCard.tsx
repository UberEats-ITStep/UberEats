import type { FC } from 'react';
import { Link } from 'react-router-dom';
import type { Order } from '../types/order.types';
import OrderStatusBadge from './OrderStatusBadge';
import { Card } from '../../../components/common';
import OrderSummaryList, { type SummaryItem } from './OrderSummaryList';
import { useRestaurantDetails } from '../../restaurants/hooks/useRestaurantDetails';
import { formatPrice } from '../../../utils/currency';

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
    const { restaurant, isLoading } = useRestaurantDetails(order.restaurant?.toString());

    // Map order items to SummaryItem, looking up names if restaurant is loaded
    const summaryItems: SummaryItem[] = order.items.map((item) => {
        let name = `Item #${item.menu_item}`;
        if (restaurant) {
            for (const category of restaurant.categories) {
                const found = category.menu_items.find(i => i.id === item.menu_item);
                if (found) {
                    name = found.name;
                    break;
                }
            }
        }
        return {
            id: item.id,
            name,
            quantity: item.quantity,
            price: item.price,
        };
    });

    const showPlaceholder = !restaurant?.image_url;

    if (isLoading) {
        return (
            <Card elevation="subtle" padding="md" className="animate-pulse">
                <div className="flex gap-4">
                    <div className="h-16 w-16 bg-border-default rounded-md"></div>
                    <div className="flex-1 space-y-3">
                        <div className="h-5 w-1/3 bg-border-default rounded"></div>
                        <div className="h-4 w-1/4 bg-border-default rounded"></div>
                    </div>
                </div>
            </Card>
        );
    }

    return (
        <Card elevation="subtle" padding="md">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex items-center gap-4">
                    <div className="h-16 w-16 shrink-0 overflow-hidden rounded-md border border-border-default bg-surface">
                        {showPlaceholder ? (
                            <div className="flex h-full w-full items-center justify-center bg-secondary text-2xl">
                                🍽️
                            </div>
                        ) : (
                            <img 
                                src={restaurant.image_url} 
                                alt={restaurant.name}
                                className="h-full w-full object-cover"
                            />
                        )}
                    </div>
                    <div>
                        <p className="text-caption text-text-muted mb-1">Order #{order.id}</p>
                        <h2 className="text-xl font-bold text-text-primary">
                            {order.restaurant ? (
                                <Link to={`/restaurants/${order.restaurant}`} className="hover:text-accent transition-colors">
                                    {restaurant?.name ?? 'Restaurant unavailable'}
                                </Link>
                            ) : (
                                'Restaurant unavailable'
                            )}
                        </h2>
                        <p className="mt-1 text-sm text-text-secondary">{formatOrderDate(order.created_at)}</p>
                    </div>
                </div>
                <div className="flex shrink-0">
                    <OrderStatusBadge status={order.status} />
                </div>
            </div>

            <div className="my-5 border-y border-border-default py-4">
                <OrderSummaryList items={summaryItems} maxDisplay={2} />
            </div>

            <div className="flex items-center justify-between gap-4">
                <span className="font-semibold text-text-secondary">Total</span>
                <span className="text-xl font-bold text-text-primary">{formatPrice(order.total_price)}</span>
            </div>
        </Card>
    );
};

export default OrderCard;