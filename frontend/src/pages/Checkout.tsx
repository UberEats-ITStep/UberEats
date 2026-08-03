import { useState } from 'react';
import type { FC } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../features/orders/api/order.service';
import { Button, Input, SectionContainer, EmptyState, Alert, Card, FormField } from '../components/common';
import OrderSummaryList, { type SummaryItem } from '../features/orders/components/OrderSummaryList';
import { formatPrice } from '../utils/currency';

const Checkout: FC = () => {
  const { cart, cartTotal, itemCount, refreshCart } = useCart();
  const { profile } = useAuth();
  const navigate = useNavigate();

  const [address, setAddress] = useState(profile?.address || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  if (!cart || cart.items.length === 0) {
    return (
      <SectionContainer width="content" padding="lg">
        <EmptyState
          title="Your cart is empty"
          description="You need to add items to your cart before checking out."
          action={
            <Button onClick={() => navigate('/')}>
              Browse Restaurants
            </Button>
          }
        />
      </SectionContainer>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) {
      setError('Please provide a delivery address.');
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await orderService.checkout(address);
      
      await refreshCart();
      
      setShowSuccess(true);
      setTimeout(() => {
        navigate('/orders', { state: { successMessage: 'Order placed successfully!' } });
      }, 1500);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { non_field_errors?: string[] } } };
      setError(error.response?.data?.non_field_errors?.[0] || 'Failed to place order. Please try again.');
      setIsSubmitting(false);
    }
  };

  const summaryItems: SummaryItem[] = cart.items.map((item) => ({
    id: item.id,
    name: item.menu_item_detail.name,
    quantity: item.quantity,
    price: parseFloat(item.menu_item_detail.price) * item.quantity,
  }));

  return (
    <SectionContainer width="content" padding="lg" className="pb-16">
      <div className="mb-6">
        <Link to="/" className="text-sm font-medium text-text-secondary hover:text-accent">
          ← Back to browsing
        </Link>
      </div>

      <h1 className="text-page-title mb-8">Checkout</h1>

      {showSuccess && (
        <div className="mb-8">
          <Alert variant="success" title="Success!" message="Your order has been placed. Redirecting..." />
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        
        {/* Checkout Form */}
        <div className="lg:col-span-7 xl:col-span-8 space-y-6">
          <Card elevation="subtle" padding="md">
            <h2 className="text-xl font-bold text-text-primary mb-6">Delivery Details</h2>
            
            {error && (
              <div className="mb-6">
                <Alert variant="error" title="Checkout Error" message={error} />
              </div>
            )}

            <form id="checkout-form" onSubmit={handleSubmit} className="space-y-6">
              <FormField label="Delivery Address" id="address" required>
                <Input
                  id="address"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="123 Main St, Apt 4B"
                  required
                  disabled={isSubmitting || showSuccess}
                />
              </FormField>
            </form>
          </Card>

          {/* Placeholders for future extensibility */}
          <Card elevation="subtle" padding="md" className="opacity-70 pointer-events-none">
            <h2 className="text-lg font-bold text-text-primary mb-4">Payment Method</h2>
            <p className="text-sm text-text-muted">Payment is handled securely upon delivery.</p>
          </Card>
          
          <Card elevation="subtle" padding="md" className="opacity-70 pointer-events-none">
            <h2 className="text-lg font-bold text-text-primary mb-4">Delivery Notes</h2>
            <p className="text-sm text-text-muted">Leave instructions for the courier (Coming soon).</p>
          </Card>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-5 xl:col-span-4">
          <div className="sticky top-24">
            <Card elevation="subtle" padding="md">
              <h2 className="text-xl font-bold text-text-primary mb-6">Order Summary</h2>
              
              <div className="mb-6 pb-6 border-b border-border-default">
                <OrderSummaryList items={summaryItems} />
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-sm text-text-secondary">
                  <p>Subtotal ({itemCount} items)</p>
                  <p>{formatPrice(cartTotal)}</p>
                </div>
                <div className="flex justify-between text-sm text-text-secondary">
                  <p>Delivery Fee</p>
                  <p className="italic">Calculated after dispatch</p>
                </div>
                <div className="flex justify-between text-lg font-bold text-text-primary pt-3 border-t border-border-default">
                  <p>Total</p>
                  <p>{formatPrice(cartTotal)}</p>
                </div>
              </div>

              <Button
                type="submit"
                form="checkout-form"
                variant="accent"
                fullWidth
                size="lg"
                disabled={isSubmitting || showSuccess}
              >
                {isSubmitting ? 'Placing Order...' : 'Place Order'}
              </Button>
            </Card>
          </div>
        </div>
      </div>
    </SectionContainer>
  );
};

export default Checkout;
