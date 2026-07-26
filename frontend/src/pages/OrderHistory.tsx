import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import OrderCard from '../features/orders/components/OrderCard';
import { orderService } from '../features/orders/api/order.service';
import type { Order } from '../features/orders/types/order.types';
import { SectionContainer, LoadingState, EmptyState, Alert } from '../components/common';

const OrderHistory: FC = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [requestError, setRequestError] = useState<string | null>(null);

    const loadOrders = useCallback(async () => {
        setIsLoading(true);
        setRequestError(null);

        try {
            const data = await orderService.getOrderHistory();
            setOrders(data);
        } catch {
            setRequestError('We could not load your orders right now. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        const controller = new AbortController();

        const loadInitialOrders = async () => {
            try {
                const data = await orderService.getOrderHistory(controller.signal);
                if (!controller.signal.aborted) {
                    setOrders(data);
                }
            } catch {
                if (!controller.signal.aborted) {
                    setRequestError('We could not load your orders right now. Please try again.');
                }
            } finally {
                if (!controller.signal.aborted) {
                    setIsLoading(false);
                }
            }
        };

        void loadInitialOrders();

        return () => controller.abort();
    }, []);

    return (
        <SectionContainer width="content" padding="lg">
            <div className="mb-8">
                <h1 className="text-page-title">Your orders</h1>
                <p className="mt-2 text-body">Review your active and previous orders.</p>
            </div>

            {isLoading ? (
                <LoadingState message="Loading your orders..." />
            ) : requestError ? (
                <Alert
                    variant="error"
                    title="Unable to load orders"
                    message={requestError}
                    onRetry={() => void loadOrders()}
                />
            ) : orders.length === 0 ? (
                <EmptyState
                    title="No orders yet"
                    description="Your completed and active orders will appear here once you place an order."
                />
            ) : (
                <div className="space-y-5">
                    {orders.map((order) => (
                        <OrderCard key={order.id} order={order} />
                    ))}
                </div>
            )}
        </SectionContainer>
    );
};

export default OrderHistory;