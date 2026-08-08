import React, { type FC } from 'react';
import Modal from '../../../components/common/Modal';
import ReviewForm from './ReviewForm';

export interface ReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (rating: number, comment: string) => Promise<void>;
  initialRating?: number;
  initialComment?: string;
  isEditing?: boolean;
}

export const ReviewModal: FC<ReviewModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialRating = 0,
  initialComment = '',
  isEditing = false,
}) => {
  const [error, setError] = React.useState<string | null>(null);

  const handleClose = () => {
    setError(null);
    onClose();
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose} 
      title={isEditing ? "Edit Review" : "Leave a Review"}
    >
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
          {error}
        </div>
      )}
      <ReviewForm
        initialRating={initialRating}
        initialComment={initialComment}
        onSubmit={async (rating, comment) => {
          try {
            setError(null);
            await onSubmit(rating, comment);
            handleClose();
          } catch (err: unknown) {
            const typedErr = err as { response?: { data?: { order?: string[]; non_field_errors?: string[] } }; message?: string };
            const errorMsg = typedErr.response?.data?.order?.[0] || typedErr.response?.data?.non_field_errors?.[0] || typedErr.message || "Something went wrong.";
            setError(errorMsg);
          }
        }}
        onCancel={handleClose}
      />
    </Modal>
  );
};

export default ReviewModal;
