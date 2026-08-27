import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import OrderCard from '../features/orders/components/OrderCard';
import { orderService } from '../features/orders/api/order.service';
import type { Order } from '../features/orders/types/order.types';
import { SectionContainer, EmptyState, Alert, Card, Button } from '../components/common';

const OrderCardSkeleton: FC = () => (
    <Card className="animate-pulse p-6 border border-border-default rounded-none">
        <div className="flex gap-4">
            <div className="h-16 w-16 bg-muted rounded-none shrink-0"></div>
            <div className="flex-1 space-y-3 py-1">
                <div className="h-5 w-1/4 bg-muted rounded-none"></div>
                <div className="h-6 w-1/2 bg-muted rounded-none"></div>
                <div className="h-4 w-1/3 bg-muted rounded-none"></div>
            </div>
            <div className="h-6 w-20 bg-muted rounded-none shrink-0"></div>
        </div>
        <div className="my-5 border-y border-border-default py-4 space-y-3">
            <div className="h-4 w-3/4 bg-muted rounded-none"></div>
            <div className="h-4 w-1/2 bg-muted rounded-none"></div>
        </div>
        <div className="flex justify-between items-center">
            <div className="h-5 w-16 bg-muted rounded-none"></div>
            <div className="h-6 w-24 bg-muted rounded-none"></div>
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

    const loadOrders = useCallback(async (silent = false) => {
        if (!silent) setIsLoading(true);
        if (!silent) setRequestError(null);

        try {
            const data = await orderService.getOrderHistory();
            setOrders(data);
        } catch {
            if (!silent) setRequestError('We could not load your orders right now. Please try again.');
        } finally {
            if (!silent) setIsLoading(false);
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

    // Polling effect for active orders
    useEffect(() => {
        const hasActiveOrders = orders.some((o) => {
          const isActive =
            o.status !== 'COMPLETED' &&
            o.status !== 'CANCELLED';
          return isActive;
        });

        if (!hasActiveOrders) return;

        const intervalId = window.setInterval(() => {
            void loadOrders(true);
        }, 10000);

        return () => window.clearInterval(intervalId);
    }, [orders, loadOrders]);

    const activeOrders = orders.filter(
        (o) => o.status !== 'COMPLETED' && o.status !== 'CANCELLED'
    );
    const pastOrders = orders.filter(
        (o) => o.status === 'COMPLETED' || o.status === 'CANCELLED'
    );

    return (
        <SectionContainer width="content" padding="lg" className="pb-16 pt-10">
            <div className="mb-12 border-b border-border-default pb-6">
                <p className="text-sm tracking-widest uppercase text-text-muted mb-2">History</p>
                <h1 className="text-5xl font-serif italic text-text-primary">Your Orders</h1>
            </div>

            {successMessage && (
                <div className="mb-8">
                    <Alert variant="success" title="Success" message={successMessage} />
                </div>
            )}

            {isLoading ? (
                <div className="space-y-6">
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
                      <Button variant="primary" onClick={() => navigate('/restaurants')}>
                        Browse Directory
                      </Button>
                    }
                />
            ) : (
                <div className="space-y-16">
                    {activeOrders.length > 0 && (
                        <div>
                            <h2 className="text-sm tracking-widest uppercase text-text-primary font-bold mb-6 flex items-center gap-2">
                                <span className="relative flex h-2.5 w-2.5">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-text-primary opacity-40"></span>
                                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-text-primary"></span>
                                </span>
                                Active Orders
                            </h2>
                            <div className="space-y-8">
                                {activeOrders.map((order) => (
                                    <OrderCard key={order.id} order={order} isActive />
                                ))}
                            </div>
                        </div>
                    )}

                    {pastOrders.length > 0 && (
                        <div>
                            <h2 className="text-sm tracking-widest uppercase text-text-muted mb-6">
                                Past Orders
                            </h2>
                            <div className="space-y-6">
                                {pastOrders.map((order) => (
                                    <OrderCard key={order.id} order={order} isActive={false} />
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </SectionContainer>
    );
};

export default OrderHistory;