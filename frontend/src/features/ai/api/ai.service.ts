import apiClient from '../../../api/client';
import type { AIRecommendationResponse } from '../types/ai.types';

export const aiService = {
  getRecommendations: async (query: string, signal?: AbortSignal): Promise<AIRecommendationResponse> => {
    const response = await apiClient.post<AIRecommendationResponse>('/ai/recommend/', { query }, { signal });
    return response.data;
  },
};
