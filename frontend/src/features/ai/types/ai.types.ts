export interface AIRecommendedMenuItem {
  id: number;
  name: string;
  price: string;
  restaurant: {
    id: number;
    name: string;
  };
}

export interface AIRecommendationItem {
  menu_item: AIRecommendedMenuItem;
  reason: string;
}

export interface AIRecommendationResponse {
  message: string;
  recommendations: AIRecommendationItem[];
}
