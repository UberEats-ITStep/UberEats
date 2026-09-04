import { useCallback, useEffect, useState } from 'react';
import type { FC } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../features/orders/api/order.service';
import { Button, Input, Textarea, SectionContainer, EmptyState, Alert, Card, FormField } from '../components/common';
import OrderSummaryList, { type SummaryItem } from '../features/orders/components/OrderSummaryList';
import OrderPlacementAnimation from '../features/orders/components/OrderPlacementAnimation';
import LocationPicker, { type ResolvedLocation } from '../features/auth/components/LocationPicker';
import { authApi } from '../features/auth/api/authApi';
import type { DeliveryAddress } from '../features/auth/types/auth.types';
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
  const [savedAddresses, setSavedAddresses] = useState<DeliveryAddress[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);
  const [coordinates, setCoordinates] = useState({ latitude: 50.62, longitude: 26.25 });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [showSuccess, setShowSuccess] = useState(false);

  const applyAddress = useCallback((address: DeliveryAddress) => {
    setSelectedAddressId(address.id); setStreet(address.street); setBuilding(address.building);
    setApartment(address.apartment); setEntrance(address.entrance); setFloor(address.floor ?? '');
    setDeliveryNotes(address.delivery_notes); setContactPhone(address.contact_phone || profile?.phone_number || '');
    if (address.latitude && address.longitude) setCoordinates({ latitude: Number(address.latitude), longitude: Number(address.longitude) });
  }, [profile?.phone_number]);
  useEffect(() => { authApi.getAddresses().then((items) => { setSavedAddresses(items); const preferred = items.find((item) => item.is_default) || items[0]; if (preferred) applyAddress(preferred); }).catch(() => undefined); }, [applyAddress]);
  const resolveLocation = (location: ResolvedLocation) => { setSelectedAddressId(null); setStreet(location.street); setBuilding(location.building); setCoordinates({ latitude: location.latitude, longitude: location.longitude }); };

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
      setError('Please fix the errors in the form.');
      window.scrollTo({ top: 0, behavior: 'smooth' });
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
        delivery_latitude: coordinates.latitude.toFixed(6),
        delivery_longitude: coordinates.longitude.toFixed(6)
      });
      
      await refreshCart();
      
      setShowSuccess(true);
      setTimeout(() => {
        navigate('/orders', { state: { successMessage: 'Order placed successfully!' } });
      }, 1500);
    } catch (err: unknown) {
      const httpErr = err as { response?: { data?: Record<string, string[]> } };
      const data = httpErr.response?.data;

      if (data) {
        const newFieldErrors: Record<string, string> = {};
        let topError = 'Failed to place order. Please check the fields below.';
        const knownFields = ['street', 'building', 'apartment', 'entrance', 'floor', 'delivery_notes', 'contact_phone'];
        
        for (const key of Object.keys(data)) {
          if (Array.isArray(data[key]) && data[key].length) {
            if (key === 'non_field_errors') {
              topError = data[key][0];
            } else if (!knownFields.includes(key)) {
              topError = `${key}: ${data[key][0]}`;
            } else {
              newFieldErrors[key] = data[key][0];
            }
          }
        }
        setFieldErrors(newFieldErrors);
        setError(topError);
      } else {
        setError('Failed to place order. Please try again.');
      }

      setIsSubmitting(false);
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

            {savedAddresses.length > 0 && <div className="mb-8"><p className="text-caption">Deliver to</p><div className="mt-3 grid gap-3 sm:grid-cols-2">{savedAddresses.map((address) => <button type="button" key={address.id} onClick={() => applyAddress(address)} className={`p-4 text-left border transition-base ${selectedAddressId === address.id ? 'border-2 border-primary bg-secondary' : 'border-border-default hover:border-text-muted'}`}><span className="flex items-center justify-between gap-2 font-bold"><span>{address.label}</span><span>{selectedAddressId === address.id ? '●' : '○'}</span></span><span className="mt-2 block text-sm text-text-secondary">{address.formatted_address}</span>{address.is_default && <span className="mt-2 block text-[10px] uppercase tracking-widest">Default address</span>}</button>)}</div><Link to="/profile" className="mt-3 inline-block text-sm font-medium underline underline-offset-4">+ Add new address</Link></div>}

            {/* Interactive Map Picker */}
            <div className="mb-8">
              <h3 className="text-lg font-bold text-text-primary mb-1">Pinpoint Location</h3>
              <p className="text-sm text-text-secondary mb-4">Drag the map to your location, then click "Confirm" to auto-fill your address.</p>
              
              <LocationPicker initialAddress={[street, building].filter(Boolean).join(' ')} initialLatitude={coordinates.latitude} initialLongitude={coordinates.longitude} onResolve={resolveLocation} />
            </div>

            <form id="checkout-form" onSubmit={handleSubmit} className="space-y-6 border-t border-border-default pt-8">
              <h3 className="text-lg font-bold text-text-primary mb-1">Delivery Address</h3>
              
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
