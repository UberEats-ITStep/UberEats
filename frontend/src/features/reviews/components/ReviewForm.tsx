import { useState, type FC, type FormEvent } from 'react';
import RatingStars from './RatingStars';
import { Button } from '../../../components/common';

export interface ReviewFormProps {
  initialRating?: number;
  initialComment?: string;
  onSubmit: (rating: number, comment: string) => Promise<void>;
  onCancel: () => void;
}

export const ReviewForm: FC<ReviewFormProps> = ({
  initialRating = 0,
  initialComment = '',
  onSubmit,
  onCancel,
}) => {
  const [rating, setRating] = useState(initialRating);
  const [comment, setComment] = useState(initialComment);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (rating === 0) {
      setError('Please select a star rating.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(rating, comment);
    } catch (err) {
      const e = err as { response?: { data?: { detail?: string } } };
      setError(e.response?.data?.detail || 'An error occurred while submitting your review.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <div>
        <label className="block text-sm font-bold text-text-primary mb-3">
          Your Rating
        </label>
        <RatingStars 
          rating={rating} 
          onRatingChange={setRating} 
          isInteractive 
          size="lg" 
        />
        {error && rating === 0 && (
          <p className="mt-2 text-sm text-status-error">{error}</p>
        )}
      </div>

      <div>
        <label htmlFor="comment" className="block text-sm font-bold text-text-primary mb-2">
          Your Review (optional)
        </label>
        <textarea
          id="comment"
          rows={4}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="What did you like or dislike? How was the food?"
          className="w-full rounded-md border border-border-default bg-surface px-4 py-3 text-text-primary placeholder-slate-400 transition-colors focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent resize-none"
        />
      </div>

      {error && rating > 0 && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-status-error border border-red-100">
          {error}
        </div>
      )}

      <div className="flex justify-end gap-3 pt-4 border-t border-border-default">
        <Button 
          type="button" 
          variant="outline" 
          onClick={onCancel} 
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button 
          type="submit" 
          variant="accent" 
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Review'}
        </Button>
      </div>
    </form>
  );
};

export default ReviewForm;
