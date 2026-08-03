export type OrderStatus =
    | 'Pending'
    | 'Preparing'
    | 'Ready'
    | 'Delivering'
    | 'Completed'
    | 'Cancelled';

export interface OrderItem {
    id: number;
    menu_item: number;
    quantity: number;
    price: string;
}

export interface Order {
    id: number;
    status: OrderStatus;
    total_price: string;
    created_at: string;
    delivery_address: string;
    restaurant: number | null; // Backend returns the ID
    items: OrderItem[];
}