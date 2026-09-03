import type { FC } from 'react';
import { Link } from 'react-router-dom';
import type { Order } from '../types/order.types';
import { Card } from '../../../components/common';
import { useRestaurantDetails } from '../../restaurants/hooks/useRestaurantDetails';
import { formatPrice } from '../../../utils/currency';
import { formatOrderDate, LIFECYCLE_STEPS, getActiveStepIndex } from '../utils/order.utils';

interface OrderCardProps {
    order: Order;
    isActive?: boolean;
}

const OrderCard: FC<OrderCardProps> = ({ order, isActive = false }) => {
    const { restaurant, isLoading } = useRestaurantDetails(order.restaurant?.toString());

    const showPlaceholder = !restaurant?.image_url;
    const isCancelled = order.status === 'CANCELLED';
    const activeIndex = getActiveStepIndex(order.status);
    const activeStep = LIFECYCLE_STEPS[activeIndex];

    if (isLoading) {
        return (
            <Card className="animate-pulse p-6 border border-border-default rounded-none">
                <div className="h-16 w-full bg-muted mb-4"></div>
                <div className="h-4 w-1/2 bg-muted"></div>
            </Card>
        );
    }

    if (isActive) {
        return (
            <Card className="p-0 border-2 border-text-primary rounded-none bg-surface shadow-elevated relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-text-primary via-text-secondary to-text-primary opacity-20"></div>
                
                <div className="p-8">
                    {/* Header */}
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <p className="text-[10px] tracking-widest uppercase text-text-muted mb-1 font-bold">
                                Order #{order.id}
                            </p>
                            <h2 className="text-4xl font-serif italic text-text-primary truncate">
                                {order.restaurant ? (
                                    <Link to={`/restaurants/${order.restaurant}`} className="hover:opacity-80 transition-opacity">
                                        {restaurant?.name ?? 'Restaurant'}
                                    </Link>
                                ) : (
                                    'Restaurant'
                                )}
                            </h2>
                        </div>
                        <div className="text-right">
                            <p className="text-xs uppercase tracking-widest text-text-muted mb-1 font-bold">Total</p>
                            <p className="text-2xl font-serif italic text-text-primary">{formatPrice(order.total_price)}</p>
                        </div>
                    </div>

                    {/* Progress UI */}
                    <div className="bg-background border border-border-default p-6 mb-6">
                        <h3 className="text-xl font-bold uppercase tracking-tight text-text-primary mb-1">
                            {activeStep?.title || 'PROCESSING'}
                        </h3>
                        <p className="text-sm text-text-secondary mb-5">{activeStep?.description}</p>
                        
                        <div className="flex gap-1.5 w-full">
                            {LIFECYCLE_STEPS.map((step, idx) => {
                                const isCompleted = idx < activeIndex;
                                const isCurrent = idx === activeIndex;
                                
                                return (
                                    <div key={step.id} className="h-1.5 flex-1 bg-border-default overflow-hidden relative">
                                        <div 
                                            className={`absolute top-0 left-0 h-full bg-text-primary transition-all duration-700 ease-in-out ${
                                                isCompleted ? 'w-full' : isCurrent ? 'w-full animate-pulse-slow opacity-80' : 'w-0'
                                            }`} 
                                        />
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <div className="text-sm text-text-secondary">
                            {order.items.length} items • Placed {formatOrderDate(order.created_at)}
                        </div>
                        <Link
                            to={`/orders/${order.id}`}
                            className="inline-flex items-center justify-center bg-text-primary text-surface px-8 py-3 text-sm tracking-widest font-bold uppercase transition-transform hover:-translate-y-0.5 shadow-subtle"
                        >
                            Track order →
                        </Link>
                    </div>
                </div>
            </Card>
        );
    }

    // Past / Compact Order Layout
    return (
        <Card className={`p-6 border rounded-none transition-colors hover:border-text-primary ${isCancelled ? 'bg-error/5 border-error/20 opacity-80' : 'bg-surface border-border-default'}`}>
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="flex items-start gap-5 w-full sm:w-auto">
                    <div className="h-16 w-16 shrink-0 overflow-hidden bg-muted border-l border-b border-border-default">
                        {showPlaceholder ? (
                            <div className="flex h-full w-full items-center justify-center bg-primary text-surface opacity-50 font-serif italic text-[10px] tracking-widest">
                                BiteUp
                            </div>
                        ) : (
                            <img 
                                src={restaurant.image_url} 
                                alt={restaurant.name}
                                className={`h-full w-full object-cover transition-all duration-500 hover:scale-105 ${isCancelled ? 'grayscale opacity-70' : 'grayscale hover:grayscale-0'}`}
                            />
                        )}
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                            <h2 className="text-lg font-bold text-text-primary truncate">
                                {restaurant?.name ?? 'Restaurant'}
                            </h2>
                            {isCancelled && <span className="text-[10px] uppercase font-bold tracking-widest text-error">Cancelled</span>}
                        </div>
                        <p className="text-sm text-text-secondary mb-2">{formatOrderDate(order.created_at)}</p>
                        <p className="text-sm font-medium text-text-primary">{formatPrice(order.total_price)} • {order.items.length} items</p>
                    </div>
                </div>
                <div className="flex shrink-0 mt-2 sm:mt-0">
                    <Link
                        to={`/orders/${order.id}`}
                        className="inline-flex items-center justify-center border border-border-default px-5 py-2 text-xs font-bold uppercase tracking-widest text-text-primary transition-base hover:bg-secondary"
                    >
                        View order
                    </Link>
                </div>
            </div>
        </Card>
    );
};

export default OrderCard;
