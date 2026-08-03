import { useState, useEffect, useRef, useCallback } from 'react';
import type { FC } from 'react';
import type { Promotion } from '../types/promotion.types';
import PromotionCard from './PromotionCard';

export interface PromotionCarouselProps {
  promotions: Promotion[];
  autoScrollInterval?: number; // in milliseconds
}

export const PromotionCarousel: FC<PromotionCarouselProps> = ({ 
  promotions, 
  autoScrollInterval = 6000 
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const nextSlide = useCallback(() => {
    setCurrentIndex((prevIndex) => (prevIndex === promotions.length - 1 ? 0 : prevIndex + 1));
  }, [promotions.length]);

  const prevSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex === 0 ? promotions.length - 1 : prevIndex - 1));
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  useEffect(() => {
    if (promotions.length <= 1) return;

    if (!isHovered) {
      timerRef.current = setInterval(nextSlide, autoScrollInterval);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isHovered, nextSlide, autoScrollInterval, promotions.length]);

  if (!promotions || promotions.length === 0) {
    return null;
  }

  return (
    <div 
      className="relative w-full group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onTouchStart={() => setIsHovered(true)}
      onTouchEnd={() => setIsHovered(false)}
    >
      <div className="overflow-hidden rounded-xl">
        <div 
          className="flex transition-transform duration-500 ease-in-out"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {promotions.map((promo) => (
            <div key={promo.id} className="w-full shrink-0 flex-none">
               <PromotionCard promotion={promo} />
            </div>
          ))}
        </div>
      </div>

      {promotions.length > 1 && (
        <>
          {/* Controls - Offset outside the banner, visible on hover or always on sm+ */}
          <button
            onClick={prevSlide}
            className="absolute -left-3 sm:-left-5 top-1/2 -translate-y-1/2 flex h-10 w-10 items-center justify-center rounded-full bg-surface text-text-primary shadow-elevated transition hover:scale-110 focus:outline-none focus:ring-2 focus:ring-accent z-10 border border-border-default opacity-0 sm:opacity-100 group-hover:opacity-100"
            aria-label="Previous promotion"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <button
            onClick={nextSlide}
            className="absolute -right-3 sm:-right-5 top-1/2 -translate-y-1/2 flex h-10 w-10 items-center justify-center rounded-full bg-surface text-text-primary shadow-elevated transition hover:scale-110 focus:outline-none focus:ring-2 focus:ring-accent z-10 border border-border-default opacity-0 sm:opacity-100 group-hover:opacity-100"
            aria-label="Next promotion"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          {/* Pagination Indicators */}
          <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 space-x-2 z-10">
            {promotions.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`h-2 w-2 rounded-full transition-all ${
                  currentIndex === index ? 'bg-white w-6' : 'bg-white/40 hover:bg-white/80'
                }`}
                aria-label={`Go to promotion ${index + 1}`}
                aria-current={currentIndex === index ? 'true' : 'false'}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default PromotionCarousel;
