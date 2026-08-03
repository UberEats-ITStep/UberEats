import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../../../context/CartContext';
import { useRestaurantDetails } from '../../restaurants/hooks/useRestaurantDetails';
import { Drawer, Button, EmptyState, Alert } from '../../../components/common';
import { formatPrice } from '../../../utils/currency';

export const CartDrawer: FC = () => {
  const { cart, isDrawerOpen, setIsDrawerOpen, isLoading, error, updateQuantity, removeFromCart, cartTotal, itemCount } = useCart();
  const navigate = useNavigate();

  // Get restaurant details for the current cart
  const { restaurant } = useRestaurantDetails(cart?.restaurant?.toString());

  const handleCheckout = () => {
    setIsDrawerOpen(false);
    navigate('/checkout');
  };

  const renderContent = () => {
    if (isLoading && !cart) {
      return (
        <div className="flex h-full flex-col justify-center space-y-4 p-4 animate-pulse">
            <div className="h-6 w-1/2 bg-border-default rounded"></div>
            <div className="h-20 bg-border-default rounded"></div>
            <div className="h-20 bg-border-default rounded"></div>
        </div>
      );
    }

    if (error) {
      return <Alert variant="error" title="Error" message={error} />;
    }

    if (!cart || cart.items.length === 0) {
      return (
        <div className="flex h-full flex-col justify-center">
          <EmptyState
            title="Your cart is empty"
            description="Looks like you haven't added any delicious food yet."
            action={
              <Button onClick={() => {
                setIsDrawerOpen(false);
                navigate('/restaurants');
              }}>
                Browse Restaurants
              </Button>
            }
          />
        </div>
      );
    }

    return (
      <div className="flex flex-col gap-6">
        {restaurant && (
          <div className="border-b border-border-default pb-4">
            <p className="text-sm text-text-muted mb-1">Your order from</p>
            <h3 className="text-xl font-bold text-text-primary">{restaurant.name}</h3>
          </div>
        )}

        <ul className="divide-y divide-border-default">
          {cart.items.map((item) => (
            <li key={item.id} className="flex py-6">
              <div className="flex flex-1 flex-col justify-between">
                <div>
                  <div className="flex justify-between text-base font-medium text-text-primary">
                    <h3 className="line-clamp-2 pr-4">{item.menu_item_detail.name}</h3>
                    <p className="whitespace-nowrap font-bold">
                      {formatPrice(parseFloat(item.menu_item_detail.price))}
                    </p>
                  </div>
                </div>
                <div className="mt-4 flex flex-1 items-end justify-between">
                  {/* Quantity Controls */}
                  <div className="flex items-center gap-3 bg-secondary rounded-full px-2 py-1">
                    <button
                      type="button"
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="flex h-7 w-7 items-center justify-center rounded-full bg-surface text-text-primary shadow-sm hover:bg-border-default transition-colors focus:outline-none disabled:opacity-50"
                      disabled={isLoading}
                    >
                      -
                    </button>
                    <span className="min-w-[20px] text-center text-sm font-semibold text-text-primary">
                      {item.quantity}
                    </span>
                    <button
                      type="button"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="flex h-7 w-7 items-center justify-center rounded-full bg-surface text-text-primary shadow-sm hover:bg-border-default transition-colors focus:outline-none disabled:opacity-50"
                      disabled={isLoading}
                    >
                      +
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={() => removeFromCart(item.id)}
                    className="text-sm font-medium text-status-error hover:underline disabled:opacity-50"
                    disabled={isLoading}
                  >
                    Remove
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderFooter = () => {
    if (!cart || cart.items.length === 0) return null;

    return (
      <div className="flex flex-col gap-4">
        <div className="flex justify-between text-base font-bold text-text-primary">
          <p>Subtotal</p>
          <p>{formatPrice(cartTotal)}</p>
        </div>
        <p className="text-sm text-text-muted">
          Delivery fees and taxes calculated at checkout.
        </p>
        <Button
          variant="accent"
          fullWidth
          size="lg"
          onClick={handleCheckout}
          disabled={isLoading}
        >
          Proceed to Checkout
        </Button>
      </div>
    );
  };

  return (
    <Drawer
      isOpen={isDrawerOpen}
      onClose={() => setIsDrawerOpen(false)}
      title={`Your Order (${itemCount})`}
      footer={renderFooter()}
    >
      {renderContent()}
    </Drawer>
  );
};

export default CartDrawer;
