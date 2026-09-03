import { useState, useRef, useEffect, useCallback } from 'react';
import { aiService } from '../api/ai.service';
import type { AIRecommendationResponse } from '../types/ai.types';

export function useAIRecommendation() {
  const [data, setData] = useState<AIRecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const fetchRecommendations = useCallback(async (query: string) => {
    if (!query.trim()) return;
    
    // Abort previous request if it exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const abortController = new AbortController();
    abortControllerRef.current = abortController;
    
    setIsLoading(true);
    setError(null);

    try {
      const result = await aiService.getRecommendations(query, abortController.signal);
      
      // Only update state if this is still the active request
      if (abortControllerRef.current === abortController) {
        setData(result);
        setIsLoading(false);
      }
    } catch (err: any) {
      // Ignore abort errors
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED' || err.message?.includes('canceled')) {
        return;
      }
      
      // Only update error if this is still the active request
      if (abortControllerRef.current === abortController) {
        setError(err.response?.data?.detail || 'Failed to get recommendations. Please try again.');
        setIsLoading(false);
      }
    }
  }, []);

  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);


  return { data, isLoading, error, fetchRecommendations, reset };
}
