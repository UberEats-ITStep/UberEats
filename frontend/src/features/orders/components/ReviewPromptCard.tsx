import { useState, type FC } from 'react';
import ReviewModal from '../../reviews/components/ReviewModal';
import { reviewService } from '../../reviews/api/review.service';
import { Button } from '../../../components/common';
import type { Order } from '../types/order.types';

export interface ReviewPromptCardProps {
  order: Order;
  onReviewed: () => void;
}

const ReviewPromptCard: FC<ReviewPromptCardProps> = ({ order, onReviewed }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!order.restaurant) return null;

  const handleSubmit = async (rating: number, comment: string) => {
    await reviewService.createReview({
      restaurant: order.restaurant as number,
      order: order.id,
      rating,
      comment,
    });
    onReviewed();
  };

  return (
    <>
      <h2 className="text-xs font-bold uppercase tracking-widest text-text-muted">Your experience</h2>
      <p className="mt-4 font-serif text-2xl italic text-text-primary">How was your order?</p>
      <Button variant="primary" className="mt-5" onClick={() => setIsModalOpen(true)}>
        Leave a review
      </Button>
      <ReviewModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
      />
    </>
  );
};

export default ReviewPromptCard;