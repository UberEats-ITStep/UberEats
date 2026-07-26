export interface Restaurant {
  id: number;
  name: string;
  description: string;
  rating: number | string | null;
  review_count: number;
  delivery_time: number | null;
  address: string;
  latitude: string | null;
  longitude: string | null;
  cuisine: number;
  cuisine_name: string;
  image_url: string;
  is_open_now: boolean;
}

export interface MenuItem {
  id: number;
  category: number;
  category_name: string;
  name: string;
  description: string;
  price: string;
  image: string | null;
  is_available: boolean;
  unavailable_reason: string;
}

export interface MenuCategory {
  id: number;
  name: string;
  menu_items: MenuItem[];
}

export interface RestaurantDetails extends Restaurant {
  categories: MenuCategory[];
}
