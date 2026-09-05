import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/common';
import { useAuth } from '../../../hooks/useAuth';
import { useRestaurantFavorite } from '../hooks/useRestaurantFavorite';

export interface FavoriteButtonProps {
  restaurantId: number;
  className?: string;
}

const HeartIcon: FC<{ filled?: boolean }> = ({ filled = false }) => (
  <svg
    viewBox="0 0 24 24"
    aria-hidden="true"
    className="h-4 w-4"
    fill={filled ? 'currentColor' : 'none'}
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 21s-7.5-4.35-9.75-8.2C.56 10.18 1.76 5 6.42 5c2.33 0 3.56 1.1 4.08 2.07C11.02 6.1 12.25 5 14.58 5c4.66 0 5.86 5.18 4.17 7.8C19.5 16.65 12 21 12 21Z" />
  </svg>
);

const FavoriteButton: FC<FavoriteButtonProps> = ({ restaurantId, className = '' }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { isFavorite, isLoading, toggleFavorite } = useRestaurantFavorite(restaurantId);

  const handleClick = async () => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    await toggleFavorite();
  };

  return (
    <Button
      type="button"
      variant={isFavorite ? 'secondary' : 'outline'}
      size="sm"
      className={className}
      leftIcon={<HeartIcon filled={isFavorite} />}
      onClick={handleClick}
      isLoading={isLoading}
      aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
      title={isAuthenticated ? (isFavorite ? 'Remove from favorites' : 'Add to favorites') : 'Log in to save favorites'}
    >
      {isFavorite ? 'Saved' : 'Save'}
    </Button>
  );
};

export default FavoriteButton;
