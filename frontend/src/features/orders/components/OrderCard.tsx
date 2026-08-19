import type { FC } from 'react';
import { Link } from 'react-router-dom';
import type { Order } from '../types/order.types';
import OrderStatusBadge from './OrderStatusBadge';
import { Card } from '../../../components/common';
import OrderSummaryList, { type SummaryItem } from './OrderSummaryList';
import { useRestaurantDetails } from '../../restaurants/hooks/useRestaurantDetails';
import { formatPrice } from '../../../utils/currency';
import { formatOrderDate } from '../utils/order.utils';

interface OrderCardProps {
    order: Order;
}

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
            <Card className="animate-pulse p-6 border border-border-default rounded-none">
                <div className="flex gap-4">
                    <div className="h-16 w-16 bg-muted rounded-none"></div>
                    <div className="flex-1 space-y-3">
                        <div className="h-5 w-1/3 bg-muted rounded-none"></div>
                        <div className="h-4 w-1/4 bg-muted rounded-none"></div>
                    </div>
                </div>
            </Card>
        );
    }

    return (
        <Card className="p-8 border border-border-default rounded-none bg-surface transition-colors hover:border-text-primary">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex items-center gap-6">
                    <div className="h-20 w-20 shrink-0 overflow-hidden bg-muted border-l border-b border-border-default">
                        {showPlaceholder ? (
                            <div className="flex h-full w-full items-center justify-center bg-primary text-surface opacity-50 font-serif italic text-xs tracking-widest">
                                BiteUp
                            </div>
                        ) : (
                            <img 
                                src={restaurant.image_url} 
                                alt={restaurant.name}
                                className="h-full w-full object-cover grayscale transition-all duration-500 hover:grayscale-0"
                            />
                        )}
                    </div>
                    <div>
                        <p className="text-xs tracking-widest uppercase text-text-muted mb-1">Order #{order.id}</p>
                        <h2 className="text-2xl font-bold text-text-primary">
                            {order.restaurant ? (
                                <Link to={`/restaurants/${order.restaurant}`} className="hover:opacity-80 transition-opacity">
                                    {restaurant?.name ?? 'Restaurant unavailable'}
                                </Link>
                            ) : (
                                'Restaurant unavailable'
                            )}
                        </h2>
                        <p className="mt-1 text-lg font-serif italic text-text-secondary">{formatOrderDate(order.created_at)}</p>
                    </div>
                </div>
                <div className="flex shrink-0 mt-2 sm:mt-0">
                    <OrderStatusBadge status={order.status} />
                </div>
            </div>

            <div className="my-6 border-y border-border-default py-6">
                <OrderSummaryList items={summaryItems} maxDisplay={2} />
            </div>

            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <span className="text-sm tracking-widest uppercase text-text-secondary font-medium">Total Amount</span>
                    <span className="ml-4 text-2xl font-serif italic text-text-primary">{formatPrice(order.total_price)}</span>
                </div>
                <Link
                    to={`/orders/${order.id}`}
                    className="inline-flex items-center justify-center border border-border-default px-5 py-2.5 text-sm font-medium text-text-primary transition-base hover:bg-secondary"
                >
                    View order
                </Link>
            </div>
        </Card>
    );
};

export default OrderCard;
