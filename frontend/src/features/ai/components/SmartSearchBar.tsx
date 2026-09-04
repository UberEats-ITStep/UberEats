import { useState, useRef, useEffect } from 'react';
import type { FC, ChangeEvent, FormEvent } from 'react';
import { useSearchParams, useLocation, useNavigate } from 'react-router-dom';
import Input from '../../../components/common/Input';
import { useAIRecommendation } from '../hooks/useAIRecommendation';
import { AIRecommendationPanel } from './AIRecommendationPanel';

export const SmartSearchBar: FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [isAiMode, setIsAiMode] = useState(false);
  const [localQuery, setLocalQuery] = useState('');
  
  const { data, isLoading, error, fetchRecommendations, reset } = useAIRecommendation();
  const containerRef = useRef<HTMLDivElement>(null);

  // Sync normal search query from URL when not in AI mode
  useEffect(() => {
    if (!isAiMode) {
      setLocalQuery(searchParams.get('q') || '');
    }
  }, [searchParams, isAiMode]);

  // Click outside to close AI panel
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        reset();
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [reset]);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocalQuery(value);

    if (!isAiMode) {
      // Normal search behavior: update URL params immediately
      if (value) {
        setSearchParams({ q: value });
        if (location.pathname !== '/' && location.pathname !== '/restaurants') {
           navigate(`/?q=${encodeURIComponent(value)}`);
        }
      } else {
        searchParams.delete('q');
        setSearchParams(searchParams);
      }
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (isAiMode && localQuery.trim() && !isLoading) {
      void fetchRecommendations(localQuery);
    }
  };

  const toggleAiMode = () => {
    const newMode = !isAiMode;
    setIsAiMode(newMode);
    setLocalQuery('');
    reset();
    
    // Clear normal search if switching to AI mode
    if (newMode) {
      if (searchParams.has('q')) {
        searchParams.delete('q');
        setSearchParams(searchParams);
      }
    }
  };

  return (
    <div ref={containerRef} className="relative w-full">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="relative w-full flex items-center">
          <Input
            type="text"
            placeholder={isAiMode ? "Describe what you're craving..." : "Search restaurants..."}
            aria-label={isAiMode ? "AI semantic search" : "Search restaurants"}
            value={localQuery}
            onChange={handleInputChange}
            className={`w-full pr-[100px] transition-colors ${
              isAiMode 
                ? 'bg-surface border-text-primary focus:border-text-primary focus:ring-1 focus:ring-text-primary' 
                : 'bg-secondary border-transparent focus:bg-surface focus:border-border-focus'
            }`}
            leftIcon={
              isAiMode ? (
                <span className="text-xl">✨</span>
              ) : (
                <svg className="h-4 w-4 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              )
            }
          />
          
          {/* AI Toggle Button */}
          <div className="absolute right-1 flex items-center gap-1">
            {isAiMode && (
              <button
                type="submit"
                disabled={isLoading || !localQuery.trim()}
                className="p-2 text-text-primary hover:bg-secondary disabled:opacity-50 transition-colors"
                aria-label="Submit AI request"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            )}
            <button
              type="button"
              onClick={toggleAiMode}
              className={`px-3 py-1.5 text-xs font-bold tracking-widest uppercase transition-colors border-l border-transparent ${
                isAiMode 
                  ? 'text-surface bg-text-primary hover:opacity-90' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-secondary'
              }`}
            >
              AI Mode
            </button>
          </div>
        </div>
      </form>

      {/* Recommendations Dropdown */}
      <AIRecommendationPanel 
        data={data} 
        isLoading={isLoading} 
        error={error} 
        onClose={reset} 
      />
    </div>
  );
};
