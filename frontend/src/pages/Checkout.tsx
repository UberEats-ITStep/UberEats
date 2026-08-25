import { useState } from 'react';
import type { FC } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../features/orders/api/order.service';
import { Button, Input, Textarea, SectionContainer, EmptyState, Alert, Card, FormField } from '../components/common';
import OrderSummaryList, { type SummaryItem } from '../features/orders/components/OrderSummaryList';
import OrderPlacementAnimation from '../features/orders/components/OrderPlacementAnimation';
import { formatPrice } from '../utils/currency';

const Checkout: FC = () => {
  const { cart, cartTotal, itemCount, refreshCart } = useCart();
  const { profile } = useAuth();
  const navigate = useNavigate();

  const [street, setStreet] = useState(profile?.address || '');
  const [building, setBuilding] = useState('');
  const [apartment, setApartment] = useState('');
  const [entrance, setEntrance] = useState('');
  const [floor, setFloor] = useState<number | ''>('');
  const [deliveryNotes, setDeliveryNotes] = useState('');
  const [contactPhone, setContactPhone] = useState(profile?.phone_number || '');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [showSuccess, setShowSuccess] = useState(false);

  if (isSubmitting || showSuccess) {
    return (
      <SectionContainer width="content" padding="lg" className="min-h-[70vh] flex items-center justify-center">
        <OrderPlacementAnimation isSuccess={showSuccess} />
      </SectionContainer>
    );
  }

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
    const errors: Record<string, string> = {};
    if (!street.trim()) errors.street = 'Street is required.';
    if (!building.trim()) errors.building = 'Building / house number is required.';

    if (Object.keys(errors).length) {
      setFieldErrors(errors);
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      setFieldErrors({});
      await orderService.checkout({
        street: street.trim(),
        building: building.trim(),
        apartment: apartment.trim(),
        entrance: entrance.trim(),
        floor: floor === '' ? null : Number(floor),
        delivery_notes: deliveryNotes.trim(),
        contact_phone: contactPhone.trim(),
      });
      
      await refreshCart();
      
      setShowSuccess(true);
      setTimeout(() => {
        navigate('/orders', { state: { successMessage: 'Order placed successfully!' } });
      }, 1500);
    } catch (err: unknown) {
      const httpErr = err as { response?: { data?: any } };
      const data = httpErr.response?.data;

      if (data) {
        const newFieldErrors: Record<string, string> = {};
        for (const key of Object.keys(data)) {
          if (Array.isArray(data[key]) && data[key].length) {
            if (key === 'non_field_errors') {
              setError(data[key][0]);
            } else {
              newFieldErrors[key] = data[key][0];
            }
          }
        }
        setFieldErrors(newFieldErrors);
      } else {
        setError('Failed to place order. Please try again.');
      }

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
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField label="Street" id="street" required error={fieldErrors.street}>
                  <Input
                    id="street"
                    value={street}
                    onChange={(e) => setStreet(e.target.value)}
                    placeholder="Soborna Street"
                    required
                  />
                </FormField>

                <FormField label="Building / House #" id="building" required error={fieldErrors.building}>
                  <Input
                    id="building"
                    value={building}
                    onChange={(e) => setBuilding(e.target.value)}
                    placeholder="15A"
                    required
                  />
                </FormField>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <FormField label="Apartment" id="apartment" optionalLabel>
                  <Input id="apartment" value={apartment} onChange={(e) => setApartment(e.target.value)} placeholder="42" />
                </FormField>

                <FormField label="Entrance" id="entrance" optionalLabel>
                  <Input id="entrance" value={entrance} onChange={(e) => setEntrance(e.target.value)} placeholder="2" />
                </FormField>

                <FormField label="Floor" id="floor" optionalLabel>
                  <Input id="floor" type="number" value={floor === '' ? '' : String(floor)} onChange={(e) => setFloor(e.target.value === '' ? '' : Number(e.target.value))} placeholder="5" />
                </FormField>
              </div>

              <FormField label="Delivery Notes" id="delivery_notes" optionalLabel helperText="Max 500 characters" error={fieldErrors.delivery_notes}>
                <Textarea id="delivery_notes" value={deliveryNotes} onChange={(e) => setDeliveryNotes(e.target.value)} rows={4} placeholder="Please call when you arrive." />
              </FormField>

              <FormField label="Contact Phone" id="contact_phone" optionalLabel error={fieldErrors.contact_phone}>
                <Input id="contact_phone" type="tel" inputMode="tel" value={contactPhone} onChange={(e) => setContactPhone(e.target.value)} placeholder="+380501234567" />
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
              >
                Place Order
              </Button>
            </Card>
          </div>
        </div>
      </div>
    </SectionContainer>
  );
};

export default Checkout;
