import type { FC } from 'react';
import type { AIRecommendationResponse } from '../types/ai.types';
import { Link } from 'react-router-dom';
import { formatPrice } from '../../../utils/currency';

interface AIRecommendationPanelProps {
  data: AIRecommendationResponse | null;
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
}

export const AIRecommendationPanel: FC<AIRecommendationPanelProps> = ({
  data,
  isLoading,
  error,
  onClose
}) => {
  if (!data && !isLoading && !error) return null;

  return (
    <div className="absolute top-full left-0 right-0 mt-2 bg-surface border border-border-default shadow-elevated z-50 max-h-[70vh] overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-surface/90 backdrop-blur-md border-b border-border-default px-5 py-4 flex justify-between items-center z-10">
        <div className="flex items-center gap-2">
          <span className="text-xl">✨</span>
          <h3 className="font-bold text-sm uppercase tracking-widest text-text-primary">
            AI Recommendations
          </h3>
        </div>
        <button 
          onClick={onClose}
          className="text-text-muted hover:text-text-primary p-1 transition-colors"
          aria-label="Close recommendations"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="p-5">
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-10 space-y-4">
            <div className="relative flex h-8 w-8 items-center justify-center">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-text-primary opacity-20"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-text-primary"></span>
            </div>
            <p className="text-sm font-medium text-text-secondary animate-pulse">
              Finding the perfect options for you...
            </p>
          </div>
        )}

        {error && (
          <div className="text-center py-8">
            <p className="text-status-error mb-2">Something went wrong.</p>
            <p className="text-sm text-text-secondary">{error}</p>
          </div>
        )}

        {!isLoading && !error && data && (
          <div className="space-y-6 animate-fade-in">
            {/* AI Explanation */}
            <div className="bg-secondary/50 p-4 border-l-2 border-text-primary">
              <p className="text-sm leading-relaxed text-text-primary font-medium">
                {data.message}
              </p>
            </div>

            {/* Results */}
            {data.recommendations.length > 0 ? (
              <div className="space-y-4">
                {data.recommendations.map((item, idx) => (
                  <Link 
                    key={`${item.menu_item.id}-${idx}`}
                    to={`/restaurants/${item.menu_item.restaurant.id}`}
                    className="block group border border-border-default hover:border-text-primary transition-colors bg-surface p-4"
                    onClick={onClose}
                  >
                    <div className="flex justify-between items-start mb-2 gap-4">
                      <div>
                        <h4 className="font-bold text-text-primary group-hover:underline decoration-2 underline-offset-4">
                          {item.menu_item.name}
                        </h4>
                        <p className="text-xs font-bold uppercase tracking-wider text-text-muted mt-1">
                          From {item.menu_item.restaurant.name}
                        </p>
                      </div>
                      <span className="font-serif italic font-medium shrink-0">
                        {formatPrice(Number(item.menu_item.price))}
                      </span>
                    </div>
                    <p className="text-sm text-text-secondary line-clamp-2">
                      {item.reason}
                    </p>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-text-secondary">No strong matches found. Try modifying your request!</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
