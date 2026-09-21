import apiClient from '../../../api/client';
import type { AIRecommendationResponse } from '../types/ai.types';

export type RecommendationEventType = 'clicked' | 'added_to_cart' | 'ordered';

export const aiService = {
  getRecommendations: async (query: string, signal?: AbortSignal): Promise<AIRecommendationResponse> => {
    const response = await apiClient.post<AIRecommendationResponse>('/ai/recommend/', { query }, { signal });
    return response.data;
  },
  trackRecommendationEvent: async (
    requestId: string,
    menuItemId: number,
    eventType: RecommendationEventType,
    position: number,
  ): Promise<void> => {
    await apiClient.post('/ai/recommendation-events/', {
      request_id: requestId,
      menu_item_id: menuItemId,
      event_type: eventType,
      position,
    });
  },
};
