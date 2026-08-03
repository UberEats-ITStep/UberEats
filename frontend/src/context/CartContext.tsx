/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { cartService } from '../features/cart/api/cart.service';
import type { Cart } from '../features/cart/types/cart.types';
import { useAuth } from '../hooks/useAuth';
import { Modal, Button } from '../components/common';

interface CartContextType {
  cart: Cart | null;
  isLoading: boolean;
  error: string | null;
  isDrawerOpen: boolean;
  setIsDrawerOpen: (isOpen: boolean) => void;
  refreshCart: () => Promise<void>;
  addToCart: (menuItemId: number, quantity: number, restaurantId: number) => Promise<void>;
  updateQuantity: (cartItemId: number, quantity: number) => Promise<void>;
  removeFromCart: (cartItemId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  cartTotal: number;
  itemCount: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export const CartProvider = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated } = useAuth();
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // State for confirm clear cart dialog
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [pendingAdd, setPendingAdd] = useState<{menuItemId: number, quantity: number, restaurantId: number} | null>(null);

  const refreshCart = useCallback(async () => {
    if (!isAuthenticated) {
      setCart(null);
      return;
    }
    
    try {
      setIsLoading(true);
      setError(null);
      const fetchedCart = await cartService.getCart();
      setCart(fetchedCart);
    } catch {
      setError('Failed to load cart');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refreshCart();
  }, [refreshCart]);

  const processAddToCart = async (menuItemId: number, quantity: number, restaurantId: number) => {
    try {
      setError(null);
      setIsLoading(true);

      let currentCart = cart;
      if (!currentCart || (cart && cart.restaurant !== restaurantId)) {
         currentCart = await cartService.getCart();
         if (!currentCart) {
            currentCart = await cartService.createCart();
         }
      }

      await cartService.addCartItem(currentCart.id, { menu_item: menuItemId, quantity });
      await refreshCart();
      setIsDrawerOpen(true);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { non_field_errors?: string[] } } };
      setError(error.response?.data?.non_field_errors?.[0] || 'Failed to add item to cart');
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (menuItemId: number, quantity: number, restaurantId: number) => {
    if (!isAuthenticated) {
      setError('Please log in to add items to your cart.');
      return;
    }

    if (cart && cart.restaurant && cart.restaurant !== restaurantId) {
      setPendingAdd({ menuItemId, quantity, restaurantId });
      setShowClearConfirm(true);
      return;
    }

    await processAddToCart(menuItemId, quantity, restaurantId);
  };

  const handleConfirmClear = async () => {
    if (!pendingAdd || !cart) {
       setShowClearConfirm(false);
       return;
    }
    
    try {
      setIsLoading(true);
      await cartService.deleteCart(cart.id);
      setCart(null); 
      setShowClearConfirm(false);
      await processAddToCart(pendingAdd.menuItemId, pendingAdd.quantity, pendingAdd.restaurantId);
    } catch {
      setError('Failed to clear cart');
      setIsLoading(false);
    } finally {
      setPendingAdd(null);
    }
  };

  const handleCancelClear = () => {
    setShowClearConfirm(false);
    setPendingAdd(null);
  };

  const updateQuantity = async (cartItemId: number, quantity: number) => {
    try {
      setError(null);
      if (quantity <= 0) {
        await removeFromCart(cartItemId);
        return;
      }
      setIsLoading(true);
      await cartService.updateCartItem(cartItemId, { quantity });
      await refreshCart();
    } catch {
      setError('Failed to update quantity');
    } finally {
      setIsLoading(false);
    }
  };

  const removeFromCart = async (cartItemId: number) => {
    try {
      setError(null);
      setIsLoading(true);
      await cartService.removeCartItem(cartItemId);
      await refreshCart();
    } catch {
      setError('Failed to remove item');
    } finally {
      setIsLoading(false);
    }
  };

  const clearCart = async () => {
    if (!cart) return;
    try {
      setError(null);
      setIsLoading(true);
      await cartService.deleteCart(cart.id);
      await refreshCart();
    } catch {
      setError('Failed to clear cart');
    } finally {
      setIsLoading(false);
    }
  };

  const cartTotal = cart?.items.reduce((total, item) => {
    return total + (parseFloat(item.menu_item_detail.price) * item.quantity);
  }, 0) || 0;

  const itemCount = cart?.items.reduce((count, item) => count + item.quantity, 0) || 0;

  return (
    <CartContext.Provider
      value={{
        cart,
        isLoading,
        error,
        isDrawerOpen,
        setIsDrawerOpen,
        refreshCart,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        cartTotal,
        itemCount,
      }}
    >
      {children}
      
      <Modal 
        isOpen={showClearConfirm} 
        onClose={handleCancelClear} 
        title="Start a new order?"
        footer={
          <div className="flex justify-end gap-3 w-full">
            <Button variant="secondary" onClick={handleCancelClear} disabled={isLoading}>
              Cancel
            </Button>
            <Button variant="primary" onClick={() => void handleConfirmClear()} disabled={isLoading}>
              Clear cart & add
            </Button>
          </div>
        }
      >
        <p className="text-body text-text-secondary">
          Your cart contains items from another restaurant. Do you want to clear it and add this item instead?
        </p>
      </Modal>
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
