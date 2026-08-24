import type { FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Alert, Card, LoadingState, SectionContainer } from '../components/common';
import OrderItemsList from '../features/orders/components/OrderItemsList';
import OrderStatusBadge from '../features/orders/components/OrderStatusBadge';
import OrderTracker from '../features/orders/components/OrderTracker';
import { useOrderTracking } from '../features/orders/hooks/useOrderTracking';
import { formatOrderDate } from '../features/orders/utils/order.utils';
import { formatPrice } from '../utils/currency';

const OrderDetails: FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const { order, isLoading, error, backgroundError, reload } = useOrderTracking(orderId);

  if (isLoading) {
    return <LoadingState message="Loading order details..." />;
  }

  if (error || !order) {
    return (
      <SectionContainer width="content" padding="lg" className="py-12">
        <Alert
          variant="error"
          title="Order unavailable"
          message={error ?? 'This order is not available.'}
          onRetry={orderId ? () => reload() : undefined}
        />
        <Link to="/orders" className="mt-6 inline-block text-sm font-medium underline underline-offset-4">
          Back to your orders
        </Link>
      </SectionContainer>
    );
  }

  return (
    <SectionContainer width="content" padding="lg" className="pb-16 pt-10">
      <Link to="/orders" className="mb-8 inline-block text-sm text-text-secondary underline underline-offset-4">
        ← Back to your orders
      </Link>

      <header className="mb-8 flex flex-col gap-5 border-b border-border-default pb-6 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-sm uppercase tracking-widest text-text-muted">Order #{order.id}</p>
          <h1 className="font-serif text-4xl italic text-text-primary sm:text-5xl">
            {order.restaurant_name ?? 'Restaurant order'}
          </h1>
          <p className="mt-3 text-text-secondary">Placed {formatOrderDate(order.created_at)}</p>
        </div>
        <OrderStatusBadge status={order.status} />
      </header>

      {backgroundError && (
        <div className="mb-8 rounded-none border border-warning bg-warning/10 p-3 text-sm text-warning">
          {backgroundError}
        </div>
      )}

      <OrderTracker order={order} />

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_22rem]">
        <Card padding="lg" className="rounded-none">
          <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted">Ordered items</h2>
          <OrderItemsList items={order.items} />
        </Card>

        <div className="space-y-8">
          <Card padding="lg" className="rounded-none">
            <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted">Delivery</h2>
            <p className="mt-4 text-lg text-text-primary">
              {order.delivery_address || 'No delivery address was provided.'}
            </p>
            {order.restaurant && (
              <Link
                to={`/restaurants/${order.restaurant}`}
                className="mt-5 inline-block text-sm font-medium underline underline-offset-4"
              >
                View restaurant
              </Link>
            )}
          </Card>

          <Card padding="lg" className="rounded-none">
            <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted">Payment summary</h2>
            <div className="mt-5 flex items-center justify-between border-b border-border-default pb-4 text-text-secondary">
              <span>Items subtotal</span>
              <span>{formatPrice(order.total_price)}</span>
            </div>
            <div className="flex items-center justify-between pt-5">
              <span className="font-bold text-text-primary">Order total</span>
              <span className="font-serif text-2xl italic text-text-primary">{formatPrice(order.total_price)}</span>
            </div>
          </Card>
        </div>
      </div>
    </SectionContainer>
  );
};

export default OrderDetails;
