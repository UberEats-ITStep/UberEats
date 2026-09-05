export interface FavoriteRestaurantDetail {
  id: number;
  name: string;
  description: string;
  image_url: string;
  address: string;
  latitude: string | null;
  longitude: string | null;
  cuisine: number;
  cuisine_name: string;
  rating: number | string | null;
  review_count: number;
  delivery_time: number | null;
  is_open_now: boolean;
}

export interface Favorite {
  id: number;
  user: number;
  restaurant: number;
  restaurant_detail: FavoriteRestaurantDetail;
  created_at: string;
}

export interface FavoriteCheckResponse {
  restaurant: number;
  is_favorite: boolean;
}
