import { useState, type FC } from 'react';
import type { Restaurant } from '../../restaurants/types/restaurant.types';
import type { Review } from '../types/review.types';
import { useAuth } from '../../../hooks/useAuth';
import { useReviews } from '../hooks/useReviews';
import { useEligibleReviewOrder } from '../hooks/useEligibleReviewOrder';
import ReviewCard from './ReviewCard';
import ReviewModal from './ReviewModal';
import { Button, EmptyState, Alert, Modal, LoadingState } from '../../../components/common';

export interface ReviewListProps {
  restaurant: Restaurant;
  onReviewChange?: () => void;
}

export const ReviewList: FC<ReviewListProps> = ({ restaurant, onReviewChange }) => {
  const { profile, isAuthenticated } = useAuth();
  const userId = profile?.id;

  const { reviews, isLoading, error, hasMore, isLoadingMore, addReview, updateReview, deleteReview, loadMore, reload } = useReviews(restaurant.id);
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
    <div className="py-16">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-6 mb-10 border-b border-text-primary pb-4">
        <div>
          <h2 className="text-3xl font-serif italic text-text-primary mb-2">Curated Feedback</h2>
          {restaurant.review_count > 0 ? (
            <div className="flex items-center gap-3">
              <span className="font-serif italic text-lg text-text-primary">
                ★ {Number(restaurant.rating).toFixed(1)}
              </span>
              <span className="text-text-muted text-sm tracking-widest uppercase font-medium">
                ({restaurant.review_count} {restaurant.review_count === 1 ? 'review' : 'reviews'})
              </span>
            </div>
          ) : (
            <p className="text-text-secondary text-sm uppercase tracking-widest">No feedback yet.</p>
          )}
        </div>

        <div>
          {!isAuthenticated ? (
            <p className="text-sm text-text-muted font-serif italic">Log in to leave a review.</p>
          ) : eligibleOrderId ? (
            <Button variant="primary" onClick={handleOpenCreateModal}>
              Write a Review
            </Button>
          ) : (
            <p className="text-sm text-text-muted font-serif italic max-w-xs text-right">
              Only verified orders can leave feedback.
            </p>
          )}
        </div>
      </div>

      {successMessage && (
        <div className="mb-8">
          <Alert variant="success" title="Feedback Recorded" message={successMessage} />
        </div>
      )}

      {isLoading && <LoadingState message="Loading reviews..." />}

      {!isLoading && error && (
        <Alert variant="error" title="Reviews couldn't be loaded right now." message={error} onRetry={reload} />
      )}

      {!isLoading && !error && !hasReviews && (
        <EmptyState
          title="No feedback yet"
          description="Be the first to share your experience."
          icon={
            <svg className="h-10 w-10 text-text-muted opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="square" strokeLinejoin="miter" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          }
        />
      )}

      {!isLoading && !error && hasReviews && (
        <div className="grid grid-cols-1 gap-6">
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

      {!isLoading && !error && hasMore && (
        <div className="mt-8 text-center">
          <button
            onClick={() => void loadMore()}
            disabled={isLoadingMore}
            className="text-sm font-medium text-text-muted hover:text-text-primary transition-base underline underline-offset-4 disabled:opacity-50"
          >
            {isLoadingMore ? 'Loading more...' : 'Load more reviews'}
          </button>
        </div>
      )}

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
        title="Remove Feedback"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setReviewToDelete(null)}>Cancel</Button>
            <Button variant="primary" onClick={() => void confirmDelete()} className="bg-status-error border-status-error text-white hover:bg-status-error/90 hover:border-status-error/90">Remove</Button>
          </div>
        }
      >
        <p className="text-text-primary text-lg font-serif italic">
          Are you sure you want to remove your feedback? Your review is important!
        </p>
      </Modal>
    </div>
  );
};

export default ReviewList;
