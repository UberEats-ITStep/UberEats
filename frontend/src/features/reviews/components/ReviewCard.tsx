import type { FC } from 'react';
import type { Review } from '../types/review.types';
import RatingStars from './RatingStars';
import { Button, Avatar } from '../../../components/common';

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

  const authorName = review.client_username || (review.client_email ? review.client_email.split('@')[0] : 'Anonymous');

  return (
    <div className="bg-surface rounded-none p-8 border border-border-default flex flex-col gap-5">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <Avatar avatarId={review.client_avatar} name={authorName} size="md" />
          <div>
            <h3 className="font-bold text-text-primary text-xl mb-1 leading-tight">{authorName}</h3>
            <div className="flex items-center gap-3 mt-2">
              <RatingStars rating={review.rating} size="sm" />
              <span className="text-xs uppercase tracking-widest text-text-muted">{formattedDate}</span>
            </div>
          </div>
        </div>

        {isOwner && (
          <div className="flex items-center gap-2">
            {onEdit && (
              <Button variant="ghost" size="sm" onClick={() => onEdit(review)}>
                Edit
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(review)}
                className="text-status-error hover:bg-secondary"
              >
                Delete
              </Button>
            )}
          </div>
        )}
      </div>

      {review.comment && (
        <p className="font-serif italic text-lg text-text-secondary leading-relaxed">
          {review.comment}
        </p>
      )}
    </div>
  );
};

export default ReviewCard;