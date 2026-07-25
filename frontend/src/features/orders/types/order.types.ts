export type OrderStatus =
    | 'Pending'
    | 'Preparing'
    | 'Ready'
    | 'Delivering'
    | 'Completed'
    | 'Cancelled';

export interface OrderItem {
    id: number;
    menuItemId: number;
    name: string;
    quantity: number;
    price: string;
}

export interface Order {
    id: number;
    restaurantName: string | null;
    status: OrderStatus;
    totalPrice: string;
    createdAt: string;
    itemCount: number;
    items: OrderItem[];
}