import { useState } from 'react';
import { aiService } from '../api/ai.service';
import type { AIRecommendationResponse } from '../types/ai.types';

export function useAIRecommendation() {
  const [data, setData] = useState<AIRecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await aiService.getRecommendations(query);
      setData(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
  };

  return { data, isLoading, error, fetchRecommendations, reset };
}
