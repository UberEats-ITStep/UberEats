import { useState, useRef, useEffect, useCallback } from 'react';
import type { FC, ChangeEvent, FormEvent } from 'react';
import { useSearchParams, useLocation, useNavigate } from 'react-router-dom';
import { useAIRecommendation } from '../hooks/useAIRecommendation';
import { SearchSurface } from './SearchSurface';

export const SmartSearchBar: FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [isAiMode, setIsAiMode] = useState(false);
  const [localQuery, setLocalQuery] = useState('');
  
  const { data, isLoading, error, fetchRecommendations, reset } = useAIRecommendation();
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isAiMode) {
      setLocalQuery(searchParams.get('q') || '');
    }
  }, [searchParams, isAiMode]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        if (isAiMode && !localQuery) {
          setIsAiMode(false);
        }
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isAiMode, localQuery]);

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocalQuery(value);

    if (!isAiMode) {
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

  const handleRetry = useCallback(() => {
    if (localQuery.trim()) {
      void fetchRecommendations(localQuery);
    }
  }, [localQuery, fetchRecommendations]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (isAiMode && localQuery.trim() && !isLoading) {
      void fetchRecommendations(localQuery);
      inputRef.current?.blur();
    }
  };

  const toggleAiMode = () => {
    const newMode = !isAiMode;
    setIsAiMode(newMode);
    
    if (newMode) {
      setLocalQuery('');
      reset();
      if (searchParams.has('q')) {
        searchParams.delete('q');
        setSearchParams(searchParams);
      }
      setTimeout(() => inputRef.current?.focus(), 0);
    } else {
      reset();
      setLocalQuery(searchParams.get('q') || '');
    }
  };

  const handleCloseSurface = useCallback(() => {
    setIsAiMode(false);
    reset();
  }, [reset]);

  const isSurfaceOpen = isAiMode;

  return (
    <div ref={containerRef} className="relative w-full z-50 group">
      <form 
        onSubmit={handleSubmit} 
        className={`relative flex items-center transition-all duration-200 ease-in-out border bg-surface ${
          isAiMode 
            ? 'border-primary shadow-subtle' 
            : 'border-border-default hover:border-text-muted focus-within:border-primary'
        }`}
      >
        <div className="relative w-full flex items-center h-10">
          <span className="absolute left-3 flex items-center justify-center text-text-muted pointer-events-none transition-colors duration-200">
            {isAiMode ? (
              // AI Active icon - small sparkle/star from HeroIcons (not an emoji) or just a simple command-like icon
              <svg className="w-4 h-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            ) : (
              // Search icon
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            )}
          </span>
          
          <input
            ref={inputRef}
            type="text"
            placeholder={isAiMode ? "What are you in the mood for?" : "Search restaurants..."}
            aria-label={isAiMode ? "AI semantic search" : "Search restaurants"}
            value={localQuery}
            onChange={handleInputChange}
            className={`w-full h-full pl-9 pr-14 bg-transparent outline-none text-sm placeholder:text-text-muted transition-colors ${
              isAiMode ? 'text-primary' : 'text-text-primary'
            }`}
          />
          
          <div className="absolute right-1 flex items-center h-full">
            {isAiMode ? (
              <div className="flex items-center">
                {localQuery.trim() && (
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="p-1.5 mr-1 text-primary hover:text-primary-hover disabled:opacity-50 transition-colors focus:outline-none focus:ring-1 focus:ring-primary rounded-sm"
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
                  className="p-1.5 text-text-muted hover:text-text-primary transition-colors focus:outline-none focus:ring-1 focus:ring-primary rounded-sm mr-1"
                  aria-label="Exit AI Mode"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={toggleAiMode}
                className="mr-2 px-2 py-1 text-[11px] font-bold tracking-widest uppercase text-text-muted hover:text-text-primary transition-colors focus:outline-none focus:ring-1 focus:ring-primary rounded-sm border border-transparent hover:border-border-default"
                aria-label="Enter AI Mode"
              >
                AI Search
              </button>
            )}
          </div>
        </div>
      </form>

      <SearchSurface 
        isOpen={isSurfaceOpen}
        data={data}
        isLoading={isLoading}
        error={error}
        onClose={handleCloseSurface}
        onRetry={handleRetry}
        query={localQuery}
      />
    </div>
  );
};
