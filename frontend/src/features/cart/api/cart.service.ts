import apiClient from '../../../api/client';
import type { Cart, CartItem, AddCartItemPayload, UpdateCartItemPayload } from '../types/cart.types';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const cartService = {
  /**
   * Fetch the current user's cart.
   * The backend returns a list of carts (filtered to the user). We grab the first one.
   */
  async getCart(signal?: AbortSignal): Promise<Cart | null> {
    const response = await apiClient.get<Cart[] | PaginatedResponse<Cart>>('/carts/', { signal });
    
    // Safely extract from paginated or flat response
    const carts = response.data && 'results' in response.data && Array.isArray(response.data.results)
      ? response.data.results
      : (response.data as Cart[]);
      
    return carts.length > 0 ? carts[0] : null;
  },

  /**
   * Create a new cart for the authenticated user.
   */
  async createCart(): Promise<Cart> {
    const response = await apiClient.post<Cart>('/carts/', {});
    return response.data;
  },

  /**
   * Add a menu item to the cart. 
   * The backend requires the cart ID and menu_item ID.
   */
  async addCartItem(cartId: number, payload: AddCartItemPayload): Promise<CartItem> {
    const response = await apiClient.post<CartItem>('/cart-items/', {
      cart: cartId,
      ...payload
    });
    return response.data;
  },

  /**
   * Update the quantity of an existing cart item.
   */
  async updateCartItem(cartItemId: number, payload: UpdateCartItemPayload): Promise<CartItem> {
    const response = await apiClient.patch<CartItem>(`/cart-items/${cartItemId}/`, payload);
    return response.data;
  },

  /**
   * Remove an item from the cart.
   */
  async removeCartItem(cartItemId: number): Promise<void> {
    await apiClient.delete(`/cart-items/${cartItemId}/`);
  },
  
  /**
   * Clear the entire cart by deleting the cart itself (backend will recreate on next fetch if needed)
   * or by deleting all items. Here we just delete the cart instance to start fresh.
   */
  async deleteCart(cartId: number): Promise<void> {
    await apiClient.delete(`/carts/${cartId}/`);
  }
};
