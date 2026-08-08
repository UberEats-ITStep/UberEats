import { useState } from 'react';
import type { FC } from 'react';

export interface RatingStarsProps {
  rating: number;
  maxRating?: number;
  size?: 'sm' | 'md' | 'lg';
  isInteractive?: boolean;
  onRatingChange?: (rating: number) => void;
  className?: string;
}

export const RatingStars: FC<RatingStarsProps> = ({
  rating,
  maxRating = 5,
  size = 'md',
  isInteractive = false,
  onRatingChange,
  className = '',
}) => {
  const [hoverRating, setHoverRating] = useState<number | null>(null);

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-8 h-8',
  };

  const handleMouseEnter = (index: number) => {
    if (isInteractive) {
      setHoverRating(index);
    }
  };

  const handleMouseLeave = () => {
    if (isInteractive) {
      setHoverRating(null);
    }
  };

  const handleClick = (index: number) => {
    if (isInteractive && onRatingChange) {
      onRatingChange(index);
    }
  };

  const displayRating = hoverRating !== null ? hoverRating : rating;

  return (
    <div className={`flex items-center space-x-1 ${className}`} onMouseLeave={handleMouseLeave}>
      {Array.from({ length: maxRating }).map((_, i) => {
        const starValue = i + 1;
        const isFilled = starValue <= displayRating;
        const isPartial = !isFilled && starValue - 0.5 <= displayRating;

        return (
          <button
            key={i}
            type="button"
            disabled={!isInteractive}
            onMouseEnter={() => handleMouseEnter(starValue)}
            onClick={() => handleClick(starValue)}
            className={`${isInteractive ? 'cursor-pointer hover:scale-110 transition-transform' : 'cursor-default'} focus:outline-none focus:ring-0`}
            aria-label={isInteractive ? `Rate ${starValue} stars` : `${starValue} star`}
            aria-disabled={!isInteractive}
          >
            <svg
              className={`${sizeClasses[size]} ${
                isFilled || isPartial ? 'text-accent' : 'text-slate-200'
              } transition-colors`}
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              {/* If partial, we could use a half-star path or mask, but for simplicity we rely on rounding for interactive, or full color. */}
              {/* To support partial elegantly with current path, we just treat it as filled for now since the backend stores integers. */}
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </button>
        );
      })}
    </div>
  );
};

export default RatingStars;
