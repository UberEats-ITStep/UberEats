import { useState, useRef, useMemo } from 'react';
import type { FC } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../features/orders/api/order.service';
import { Button, Input, Textarea, SectionContainer, EmptyState, Alert, Card, FormField } from '../components/common';
import OrderSummaryList, { type SummaryItem } from '../features/orders/components/OrderSummaryList';
import OrderPlacementAnimation from '../features/orders/components/OrderPlacementAnimation';
import { formatPrice } from '../utils/currency';
import Map, { NavigationControl } from 'react-map-gl/maplibre';
import type { MapRef } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

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

  const maptilerKey = import.meta.env.VITE_MAPTILER_API_KEY;
  const mapRef = useRef<MapRef>(null);
  const formRef = useRef<HTMLFormElement>(null);
  
  // Default to Rivne city center
  const [viewState, setViewState] = useState({
    longitude: 26.250000,
    latitude: 50.620000,
    zoom: 14
  });

  const mapStyle = useMemo(() => {
    return maptilerKey 
      ? `https://api.maptiler.com/maps/basic-v2/style.json?key=${maptilerKey}`
      : {
          version: 8,
          sources: {
            osm: {
              type: 'raster',
              tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
              tileSize: 256,
              attribution: '&copy; OpenStreetMap Contributors',
            }
          },
          layers: [
            {
              id: 'osm',
              type: 'raster',
              source: 'osm',
              paint: {
                'raster-saturation': -1,
                'raster-opacity': 0.8
              }
            }
          ]
        } as any;
  }, [maptilerKey]);

  const handleReverseGeocode = async () => {
    if (!maptilerKey) {
      alert("MapTiler API key is missing. Manual entry required.");
      return;
    }
    
    try {
      const res = await fetch(`https://api.maptiler.com/geocoding/${viewState.longitude},${viewState.latitude}.json?key=${maptilerKey}`);
      const data = await res.json();
      
      if (data.features && data.features.length > 0) {
        const addressFeature = data.features.find((f: any) => f.place_type.includes('address')) || data.features[0];
        
        if (addressFeature.text) setStreet(addressFeature.text);
        if (addressFeature.address) setBuilding(addressFeature.address);
        
        // Provide visual feedback and scroll to form
        formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        alert("Could not find an address for this exact location.");
      }
    } catch (e) {
      console.error(e);
      alert("Failed to reverse geocode location.");
    }
  };

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
        delivery_latitude: viewState.latitude.toFixed(6),
        delivery_longitude: viewState.longitude.toFixed(6)
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

            {/* Interactive Map Picker */}
            <div className="mb-8">
              <h3 className="text-lg font-bold text-text-primary mb-1">Pinpoint Location</h3>
              <p className="text-sm text-text-secondary mb-4">Drag the map to your location, then click "Confirm" to auto-fill your address.</p>
              
              <div className="relative w-full h-[300px] sm:h-[400px] border border-border-default bg-muted shadow-subtle overflow-hidden group">
                <Map
                  ref={mapRef}
                  {...viewState}
                  onMove={evt => setViewState(evt.viewState)}
                  mapStyle={mapStyle}
                  attributionControl={false}
                >
                  <NavigationControl position="top-right" />
                  
                  {/* Minimalist Editorial Center Pin */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-full pointer-events-none z-10 flex flex-col items-center transition-transform duration-100">
                    <div className="w-8 h-8 bg-text-primary rounded-full flex items-center justify-center shadow-elevated border-4 border-surface">
                      <div className="w-2 h-2 bg-surface rounded-full" />
                    </div>
                    <div className="w-1 h-5 bg-text-primary shadow-elevated" />
                    <div className="w-2 h-2 bg-text-primary rounded-full -mt-1 opacity-40 shadow-elevated" />
                  </div>
                </Map>
                
                {/* Overlay Confirm Button */}
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20">
                  <Button 
                    type="button" 
                    variant="primary" 
                    size="md" 
                    className="shadow-elevated px-8 whitespace-nowrap transition-transform hover:scale-105 active:scale-95"
                    onClick={handleReverseGeocode}
                  >
                    Confirm Location
                  </Button>
                </div>
              </div>
              <p className="text-xs text-text-muted mt-2 text-right">
                GPS: {viewState.latitude.toFixed(5)}, {viewState.longitude.toFixed(5)}
              </p>
            </div>

            <form ref={formRef} id="checkout-form" onSubmit={handleSubmit} className="space-y-6 border-t border-border-default pt-8">
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
