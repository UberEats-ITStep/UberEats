export interface SimpleMenuItem {
  id: number;
  name: string;
  price: string;
}

export interface CartItem {
  id: number;
  cart: number;
  menu_item: number;
  quantity: number;
  menu_item_detail: SimpleMenuItem;
}

export interface Cart {
  id: number;
  user: number;
  restaurant: number | null;
  items: CartItem[];
  created_at?: string;
  updated_at?: string;
}

export interface AddCartItemPayload {
  menu_item: number;
  quantity?: number;
}

export interface UpdateCartItemPayload {
  quantity: number;
}
