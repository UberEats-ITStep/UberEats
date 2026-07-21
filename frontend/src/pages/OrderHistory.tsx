import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import OrderCard from '../features/orders/components/OrderCard';
import { orderService } from '../features/orders/api/order.service';
import type { Order } from '../features/orders/types/order.types';

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
        <section className="mx-auto w-full max-w-4xl">
            <div className="mb-8">
                <h1 className="text-3xl font-extrabold tracking-tight text-gray-900">Your orders</h1>
                <p className="mt-2 text-gray-600">Review your active and previous orders.</p>
            </div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20 text-center text-gray-600" role="status">
                    <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-gray-200 border-t-green-600" />
                    <p>Loading your orders...</p>
                </div>
            ) : requestError ? (
                <div className="rounded-lg bg-red-50 px-6 py-10 text-center" role="alert">
                    <p className="text-gray-700">{requestError}</p>
                    <button
                        type="button"
                        onClick={() => void loadOrders()}
                        className="mt-4 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                    >
                        Try again
                    </button>
                </div>
            ) : orders.length === 0 ? (
                <div className="rounded-lg bg-white px-6 py-16 text-center shadow-sm ring-1 ring-gray-200">
                    <h2 className="text-xl font-bold text-gray-900">No orders yet</h2>
                    <p className="mt-2 text-gray-600">Your completed and active orders will appear here.</p>
                </div>
            ) : (
                <div className="space-y-5">
                    {orders.map((order) => (
                        <OrderCard key={order.id} order={order} />
                    ))}
                </div>
            )}
        </section>
    );
};

export default OrderHistory;