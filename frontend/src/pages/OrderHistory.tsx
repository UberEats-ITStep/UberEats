import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import OrderCard from '../features/orders/components/OrderCard';
import { orderService } from '../features/orders/api/order.service';
import type { Order } from '../features/orders/types/order.types';
import { SectionContainer, EmptyState, Alert, Card, Button } from '../components/common';

const OrderCardSkeleton: FC = () => (
    <Card elevation="subtle" padding="md" className="animate-pulse">
        <div className="flex gap-4">
            <div className="h-16 w-16 bg-border-default rounded-md shrink-0"></div>
            <div className="flex-1 space-y-3 py-1">
                <div className="h-5 w-1/4 bg-border-default rounded"></div>
                <div className="h-6 w-1/2 bg-border-default rounded"></div>
                <div className="h-4 w-1/3 bg-border-default rounded"></div>
            </div>
            <div className="h-6 w-20 bg-border-default rounded shrink-0"></div>
        </div>
        <div className="my-5 border-y border-border-default py-4 space-y-3">
            <div className="h-4 w-3/4 bg-border-default rounded"></div>
            <div className="h-4 w-1/2 bg-border-default rounded"></div>
        </div>
        <div className="flex justify-between items-center">
            <div className="h-5 w-16 bg-border-default rounded"></div>
            <div className="h-6 w-24 bg-border-default rounded"></div>
        </div>
    </Card>
);

const OrderHistory: FC = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const successMessage = location.state?.successMessage as string | undefined;

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
        <SectionContainer width="content" padding="lg" className="pb-16">
            <div className="mb-8">
                <h1 className="text-page-title">Your orders</h1>
                <p className="mt-2 text-body">Review your active and previous orders.</p>
            </div>

            {successMessage && (
                <div className="mb-8">
                    <Alert variant="success" title="Success" message={successMessage} />
                </div>
            )}

            {isLoading ? (
                <div className="space-y-5">
                    <OrderCardSkeleton />
                    <OrderCardSkeleton />
                    <OrderCardSkeleton />
                </div>
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
                    description="Your completed and active orders will appear here once you place an order. Discover great food around you!"
                    action={
                      <Button onClick={() => navigate('/restaurants')}>
                        Browse Restaurants
                      </Button>
                    }
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