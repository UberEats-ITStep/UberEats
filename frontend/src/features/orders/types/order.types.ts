export type OrderStatus =
    | 'PENDING'
    | 'ACCEPTED'
    | 'PREPARING'
    | 'READY'
    | 'DELIVERING'
    | 'COMPLETED'
    | 'CANCELLED';

export interface OrderItem {
    id: number;
    menu_item: number;
    menu_item_name?: string;
    quantity: number;
    price: string;
    subtotal?: string;
}

export interface Order {
    id: number;
    status: OrderStatus;
    total_price: string;
    created_at: string;
    delivery_address: string;
    delivery_latitude?: string | null;
    delivery_longitude?: string | null;
    restaurant: number | null; // Backend returns the ID
    restaurant_name?: string;
    restaurant_latitude?: string | null;
    restaurant_longitude?: string | null;
    items: OrderItem[];
}
