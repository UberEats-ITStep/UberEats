import { useRef, useEffect } from 'react';
import type { FC } from 'react';
import gsap from 'gsap';
import { useGSAP } from '@gsap/react';
import type { AIRecommendationResponse } from '../types/ai.types';
import { AIRecommendationItem } from './AIRecommendationItem';

interface SearchSurfaceProps {
  isOpen: boolean;
  data: AIRecommendationResponse | null;
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
  onRetry?: () => void;
  query: string;
}

export const SearchSurface: FC<SearchSurfaceProps> = ({
  isOpen,
  data,
  isLoading,
  error,
  onClose,
  onRetry,
  query,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    let mm = gsap.matchMedia();

    mm.add("(prefers-reduced-motion: no-preference)", () => {
      if (isOpen) {
        gsap.to(containerRef.current, {
          autoAlpha: 1,
          y: 0,
          duration: 0.3,
          ease: 'power2.out',
        });
        if (contentRef.current && !isLoading && data) {
          gsap.fromTo(
            contentRef.current.children,
            { autoAlpha: 0, y: 10 },
            { autoAlpha: 1, y: 0, duration: 0.4, stagger: 0.05, ease: 'power2.out', delay: 0.1 }
          );
        }
      } else {
        gsap.to(containerRef.current, {
          autoAlpha: 0,
          y: -10,
          duration: 0.2,
          ease: 'power2.in',
        });
      }
    });

    mm.add("(prefers-reduced-motion: reduce)", () => {
      if (isOpen) {
        gsap.set(containerRef.current, { autoAlpha: 1, y: 0 });
        if (contentRef.current && !isLoading && data) {
          gsap.set(contentRef.current.children, { autoAlpha: 1, y: 0 });
        }
      } else {
        gsap.set(containerRef.current, { autoAlpha: 0, y: 0 });
      }
    });

    return () => mm.revert();
  }, [isOpen, isLoading, data]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <div
      ref={containerRef}
      className="absolute top-full left-0 right-0 mt-3 bg-surface shadow-floating z-50 max-h-[75vh] overflow-y-auto border border-border-default invisible opacity-0 origin-top"
      role="region"
      aria-live="polite"
    >
      <div className="p-6 md:p-8 min-h-[200px] flex flex-col relative">
        {/* Close Button Mobile - screen reader only mostly since desktop doesn't strictly need it, but good for a11y */}
        <button
          onClick={onClose}
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:right-4 bg-surface px-3 py-1 border border-primary z-50 text-sm"
        >
          Close AI Search
        </button>

        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center py-12 space-y-4 animate-fade-in">
            <p 
              className="text-lg md:text-xl font-serif italic bg-clip-text text-transparent animate-text-shimmer"
              style={{
                backgroundImage: 'linear-gradient(90deg, var(--color-text-primary) 0%, var(--color-text-muted) 50%, var(--color-text-primary) 100%)',
                backgroundSize: '200% auto',
              }}
            >
              BiteUp is understanding your request...
            </p>
          </div>
        )}

        {error && (
          <div className="flex-1 flex flex-col items-center justify-center py-12 text-center animate-fade-in">
            <p className="text-status-error font-medium mb-2">We couldn't process that request.</p>
            <p className="text-sm text-text-secondary mb-6 max-w-sm">{error}</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="px-4 py-2 bg-text-primary text-surface text-sm font-bold uppercase tracking-widest hover:opacity-90 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                Try Again
              </button>
            )}
          </div>
        )}

        {!isLoading && !error && data && (
          <div ref={contentRef} className="space-y-6">
            {/* AI Explanation / Leading text */}
            <div className="pb-4 border-b border-border-default">
              <h3 className="text-lg md:text-xl font-serif text-text-primary">
                {data.message}
              </h3>
            </div>

            {/* Recommendations List */}
            {data.recommendations.length > 0 ? (
              <div className="flex flex-col">
                {data.recommendations.map((item, idx) => (
                  <AIRecommendationItem
                    key={`${item.menu_item.id}-${idx}`}
                    item={item}
                    index={idx}
                    isFeatured={idx === 0 && data.recommendations.length > 1}
                    onClose={onClose}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-10">
                <p className="text-text-secondary font-medium">No strong matches found for "{query}".</p>
                <p className="text-sm text-text-muted mt-2">Try describing your craving differently.</p>
              </div>
            )}
          </div>
        )}

        {!isLoading && !error && !data && isOpen && (
          <div className="flex-1 flex flex-col items-center justify-center py-12 text-center text-text-secondary">
             <p className="font-serif italic text-lg text-text-muted">
               What are you craving?
             </p>
             <p className="text-sm mt-2 max-w-xs">
               Try "something spicy and vegetarian" or "a heavy burger with fries".
             </p>
          </div>
        )}
      </div>
    </div>
  );
};
