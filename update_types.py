import sys

filepath = 'frontend/src/features/orders/types/order.types.ts'
with open(filepath, 'r') as f:
    content = f.read()

new_order_type = """export interface Order {
    id: number;
    status: OrderStatus;
    total_price: string;
    created_at: string;
    
    // Address fields
    street: string;
    building: string;
    apartment?: string;
    entrance?: string;
    floor?: number | null;
    delivery_notes?: string;
    contact_phone?: string;
    
    // Delivery coordinates (optional, legacy orders might lack them)
    delivery_latitude?: string | null;
    delivery_longitude?: string | null;
    
    // Restaurant info
    restaurant: number | null; // Backend returns the ID
    restaurant_name?: string;
    restaurant_latitude?: string | null;
    restaurant_longitude?: string | null;
    
    items: OrderItem[];
    courier?: number | null;
}"""

import re
content = re.sub(r'export interface Order \{.*\}', new_order_type, content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(content)
