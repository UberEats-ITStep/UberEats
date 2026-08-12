import type { FC } from 'react';
import type { Review } from '../types/review.types';
import RatingStars from './RatingStars';
import { Button } from '../../../components/common';

export interface ReviewCardProps {
  review: Review;
  isOwner?: boolean;
  onEdit?: (review: Review) => void;
  onDelete?: (review: Review) => void;
}

export const ReviewCard: FC<ReviewCardProps> = ({ 
  review, 
  isOwner = false, 
  onEdit, 
  onDelete 
}) => {
  const formattedDate = new Date(review.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });

  // Fallback if client_email is missing or we only want first part
  const authorName = review.client_email ? review.client_email.split('@')[0] : 'Anonymous';

  return (
    <div className="bg-surface rounded-xl p-6 shadow-subtle border border-border-default flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-text-primary text-lg mb-1">{authorName}</h3>
          <div className="flex items-center gap-3">
            <RatingStars rating={review.rating} size="sm" />
            <span className="text-sm text-text-muted">{formattedDate}</span>
          </div>
        </div>
        
        {isOwner && (
          <div className="flex items-center gap-2">
            {onEdit && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => onEdit(review)}
                className="text-text-secondary hover:text-primary"
              >
                Edit
              </Button>
            )}
            {onDelete && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => onDelete(review)}
                className="text-status-error hover:bg-red-50 hover:text-red-700"
              >
                Delete
              </Button>
            )}
          </div>
        )}
      </div>

      {review.comment && (
        <p className="text-text-secondary leading-relaxed whitespace-pre-wrap">
          {review.comment}
        </p>
      )}
    </div>
  );
};

export default ReviewCard;
