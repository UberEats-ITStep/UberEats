import { useState, type FC } from 'react';
import type { Restaurant } from '../../restaurants/types/restaurant.types';
import type { Review } from '../types/review.types';
import { useAuth } from '../../../hooks/useAuth';
import { useReviews } from '../hooks/useReviews';
import { useEligibleReviewOrder } from '../hooks/useEligibleReviewOrder';
import RatingStars from './RatingStars';
import ReviewCard from './ReviewCard';
import ReviewModal from './ReviewModal';
import { Button, EmptyState, Alert, Modal } from '../../../components/common';

export interface ReviewListProps {
  restaurant: Restaurant;
  onReviewChange?: () => void;
}

export const ReviewList: FC<ReviewListProps> = ({ restaurant, onReviewChange }) => {
  const { profile, isAuthenticated } = useAuth();
  const userId = profile?.id;

  const { reviews, addReview, updateReview, deleteReview } = useReviews(restaurant.id);
  const { eligibleOrderId } = useEligibleReviewOrder(restaurant.id, userId, reviews);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingReview, setEditingReview] = useState<Review | null>(null);
  const [reviewToDelete, setReviewToDelete] = useState<Review | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const showSuccess = (msg: string) => {
    setSuccessMessage(msg);
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  const handleOpenCreateModal = () => {
    setEditingReview(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (review: Review) => {
    setEditingReview(review);
    setIsModalOpen(true);
  };

  const handleSubmit = async (rating: number, comment: string) => {
    if (editingReview) {
      await updateReview(editingReview.id, { rating, comment });
    } else {
      if (!eligibleOrderId) {
        throw new Error("You do not have an eligible order to review.");
      }
      await addReview({
        restaurant: restaurant.id,
        order: eligibleOrderId,
        rating,
        comment,
      });
      showSuccess("Your review was successfully posted!");
    }
    if (onReviewChange) {
      onReviewChange();
    }
  };

  const handleDeleteClick = (review: Review) => {
    setReviewToDelete(review);
  };

  const confirmDelete = async () => {
    if (reviewToDelete) {
      await deleteReview(reviewToDelete.id);
      setReviewToDelete(null);
      showSuccess("Your review was deleted.");
      if (onReviewChange) {
        onReviewChange();
      }
    }
  };

  const hasReviews = reviews.length > 0;

  return (
    <div className="py-8">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-6">
        <div>
          <h2 className="text-section-title mb-2">Customer Reviews</h2>
          {restaurant.review_count > 0 ? (
            <div className="flex items-center gap-3">
              <RatingStars rating={Math.round(Number(restaurant.rating) || 0)} />
              <span className="font-bold text-lg text-text-primary">
                {Number(restaurant.rating).toFixed(1)}
              </span>
              <span className="text-text-secondary text-sm">
                ({restaurant.review_count} {restaurant.review_count === 1 ? 'review' : 'reviews'})
              </span>
            </div>
          ) : (
            <p className="text-text-secondary">No ratings yet.</p>
          )}
        </div>

        <div>
          {!isAuthenticated ? (
            <p className="text-sm text-text-muted italic">Log in to leave a review.</p>
          ) : eligibleOrderId ? (
            <Button variant="accent" onClick={handleOpenCreateModal}>
              Leave Review
            </Button>
          ) : (
            <p className="text-sm text-text-muted italic max-w-xs text-right">
              Only customers who completed an order can leave a review.
            </p>
          )}
        </div>
      </div>

      {successMessage && (
        <div className="mb-6">
          <Alert variant="success" title="Success" message={successMessage} />
        </div>
      )}

      {/* Review List or Empty State */}
      {!hasReviews ? (
        <EmptyState
          title="No reviews yet"
          description="Be the first to share your experience with others!"
          icon={
            <svg className="h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reviews.map(review => (
            <ReviewCard
              key={review.id}
              review={review}
              isOwner={userId === review.client}
              onEdit={handleOpenEditModal}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      )}

      {/* Review Form Modal */}
      <ReviewModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleSubmit}
        initialRating={editingReview?.rating || 0}
        initialComment={editingReview?.comment || ''}
        isEditing={!!editingReview}
      />

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!reviewToDelete}
        onClose={() => setReviewToDelete(null)}
        title="Delete Review"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setReviewToDelete(null)}>Cancel</Button>
            <Button variant="danger" onClick={() => void confirmDelete()}>Delete</Button>
          </div>
        }
      >
        <p className="text-text-primary">
          Are you sure you want to delete this review? This action cannot be undone.
        </p>
      </Modal>
    </div>
  );
};

export default ReviewList;
