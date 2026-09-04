import type { FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import { SectionContainer, Card, Alert, LoadingState } from '../components/common';
import OrderItemsList from '../features/orders/components/OrderItemsList';
import OrderStatusBadge from '../features/orders/components/OrderStatusBadge';
import OrderTracker from '../features/orders/components/OrderTracker';
import { useOrderTracking } from '../features/orders/hooks/useOrderTracking';
import { formatOrderDate } from '../features/orders/utils/order.utils';
import { formatPrice } from '../utils/currency';
import ReviewPromptCard from '../features/orders/components/ReviewPromptCard';

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

  const isDelivering = order.status === 'DELIVERING';
  const isCompleted = order.status === 'COMPLETED' || order.status === 'CANCELLED';

  return (
    <SectionContainer width="page" padding="lg" className="pb-16 pt-10">
      <Link to="/orders" className="mb-8 inline-block text-xs uppercase tracking-widest text-text-secondary font-bold hover:text-text-primary transition-colors">
        ← Back to orders
      </Link>

      {backgroundError && (
        <div className="mb-8 rounded-none border border-warning bg-warning/10 p-3 text-sm text-warning">
          {backgroundError}
        </div>
      )}

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

          <OrderTracker order={order} />

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
                {(
                  (order.street && order.building && `${order.street}, ${order.building}`) ||
                  (order.street && `${order.street}`) ||
                  'No delivery address was provided.'
                )}
              </p>
              { (order.apartment || order.entrance || order.floor || order.delivery_notes || order.contact_phone) && (
                <div className="mb-4 text-sm text-text-secondary space-y-1">
                  {order.apartment && <div><span className="font-medium text-text-primary">Apt:</span> {order.apartment}</div>}
                  {order.entrance && <div><span className="font-medium text-text-primary">Entrance:</span> {order.entrance}</div>}
                  {order.floor != null && <div><span className="font-medium text-text-primary">Floor:</span> {order.floor}</div>}
                  {order.delivery_notes && <div><span className="font-medium text-text-primary">Notes:</span> {order.delivery_notes}</div>}
                  {order.contact_phone && <div><span className="font-medium text-text-primary">Phone:</span> {order.contact_phone}</div>}
                </div>
              )}
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

            {order.status === 'COMPLETED' && (
              <Card padding="lg" className="rounded-none border border-border-default">
                {order.review_id ? (
                  <p className="text-sm uppercase tracking-widest text-text-muted">Review submitted</p>
                ) : (
                  <ReviewPromptCard order={order} onReviewed={reload} />
                )}
              </Card>
            )}
          </div>
        </div>
      </div>
    </SectionContainer>
  );
};

export default OrderDetails;