export interface Review {
  id: number;
  client: number;
  client_email: string;
  restaurant: number;
  order: number;
  rating: number;
  comment: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewPayload {
  restaurant: number;
  order: number;
  rating: number;
  comment: string;
}

export interface PaginatedReviews {
  count: number;
  next: string | null;
  previous: string | null;
  results: Review[];
}
