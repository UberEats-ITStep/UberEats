import type { FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Alert, Card, LoadingState, SectionContainer } from '../components/common';
import OrderItemsList from '../features/orders/components/OrderItemsList';
import OrderStatusBadge from '../features/orders/components/OrderStatusBadge';
import { useOrderDetails } from '../features/orders/hooks/useOrderDetails';
import { formatOrderDate } from '../features/orders/utils/order.utils';
import { formatPrice } from '../utils/currency';

const OrderDetails: FC = () => {
  const { orderId } = useParams<{ orderId: string }>();
  const { order, isLoading, error, reload } = useOrderDetails(orderId);

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
          onRetry={orderId ? reload : undefined}
        />
        <Link to="/orders" className="mt-6 inline-block text-sm font-medium underline underline-offset-4">
          Back to your orders
        </Link>
      </SectionContainer>
    );
  }

  const isDelivering = order.status === 'Delivering';
  const isCompleted = order.status === 'Completed' || order.status === 'Cancelled';

  return (
    <SectionContainer width="page" padding="lg" className="pb-16 pt-10">
      <Link to="/orders" className="mb-8 inline-block text-xs uppercase tracking-widest text-text-secondary font-bold hover:text-text-primary transition-colors">
        ← Back to orders
      </Link>

      <div className="layout-grid">
        {/* Left Column: Primary Status / Map Area */}
        <div className="col-span-1 md:col-span-4 lg:col-span-8 flex flex-col gap-8">
          
          <header className={`flex flex-col border-b border-border-default pb-8 ${isDelivering ? 'mb-4' : 'mb-0'}`}>
            <p className="mb-3 text-xs uppercase tracking-widest text-text-muted font-bold">Order #{order.id}</p>
            <h1 className="font-serif italic text-text-primary text-4xl lg:text-6xl mb-4">
              {order.restaurant_name ?? 'Restaurant order'}
            </h1>
            
            <div className="flex flex-wrap items-center gap-4 mt-2">
              <OrderStatusBadge status={order.status} />
              <p className="text-text-secondary text-sm">Placed {formatOrderDate(order.created_at)}</p>
            </div>
          </header>

          {/* This is where a Map would conditionally take over if they had one */}
          {isDelivering && (
            <div className="w-full h-64 lg:h-96 bg-secondary flex items-center justify-center border border-border-default">
              <div className="text-text-muted text-sm uppercase tracking-widest font-bold">
                [ Live Delivery Map Active ]
              </div>
            </div>
          )}

          {isCompleted && (
            <div className="w-full p-8 bg-surface-muted border border-border-default">
              <h3 className="font-serif italic text-2xl text-text-primary mb-2">Order Complete</h3>
              <p className="text-text-secondary">We hope you enjoyed your meal.</p>
              <button className="mt-6 px-6 py-3 bg-primary text-surface text-xs uppercase tracking-widest font-bold hover:bg-primary-hover transition-colors">
                Reorder
              </button>
            </div>
          )}

          <div className="mt-8">
            <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-6">Ordered items</h2>
            <OrderItemsList items={order.items} />
          </div>

        </div>

        {/* Right Column: Order Details */}
        <div className="col-span-1 md:col-span-4 lg:col-span-4">
          <div className="sticky top-24 space-y-8">
            
            <Card elevation="none" padding="none" className="bg-transparent border-t border-border-default pt-6 rounded-none">
              <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-4">Delivery Details</h2>
              <p className="text-lg text-text-primary font-serif italic mb-4">
                {order.delivery_address || 'No delivery address was provided.'}
              </p>
              {order.restaurant && (
                <Link
                  to={`/restaurants/${order.restaurant}`}
                  className="text-xs uppercase tracking-widest font-bold text-text-primary hover:text-text-muted transition-colors border-b border-text-primary pb-1"
                >
                  View restaurant
                </Link>
              )}
            </Card>

            <Card elevation="none" padding="none" className="bg-transparent border-t border-border-default pt-6 rounded-none">
              <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted mb-4">Payment Summary</h2>
              <div className="flex items-center justify-between pb-4 text-text-secondary text-sm">
                <span>Items subtotal</span>
                <span>{formatPrice(order.total_price)}</span>
              </div>
              <div className="flex items-center justify-between pt-4 border-t border-border-subtle">
                <span className="text-xs uppercase tracking-widest font-bold text-text-primary">Order total</span>
                <span className="font-serif text-2xl italic text-text-primary">{formatPrice(order.total_price)}</span>
              </div>
            </Card>

          </div>
        </div>
      </div>
    </SectionContainer>
  );
};

export default OrderDetails;
