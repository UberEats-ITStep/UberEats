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
    /** Historical name captured when the order was placed. */
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
    street?: string;
    building?: string;
    apartment?: string;
    entrance?: string;
    floor?: number | null;
    delivery_notes?: string;
    contact_phone?: string;
    delivery_latitude?: string | null;
    delivery_longitude?: string | null;
    restaurant: number | null;
    /** Historical name captured when the order was placed. */
    restaurant_name?: string;
    restaurant_image_url?: string | null;
    restaurant_latitude?: string | null;
    restaurant_longitude?: string | null;
    items: OrderItem[];
    review_id: number | null;
}
