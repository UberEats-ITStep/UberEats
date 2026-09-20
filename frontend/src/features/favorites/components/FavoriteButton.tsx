import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/common';
import { useAuth } from '../../../hooks/useAuth';
import { useFavorites } from '../../../context/FavoritesContext';

export interface FavoriteButtonProps {
  restaurantId: number;
  className?: string;
  iconOnly?: boolean;
}

const HeartIcon: FC<{ filled?: boolean }> = ({ filled = false }) => (
  <svg
    viewBox="0 0 24 24"
    aria-hidden="true"
    className="h-5 w-5 transition-transform group-hover:scale-110"
    fill={filled ? 'currentColor' : 'none'}
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 21s-7.5-4.35-9.75-8.2C.56 10.18 1.76 5 6.42 5c2.33 0 3.56 1.1 4.08 2.07C11.02 6.1 12.25 5 14.58 5c4.66 0 5.86 5.18 4.17 7.8C19.5 16.65 12 21 12 21Z" />
  </svg>
);

const FavoriteButton: FC<FavoriteButtonProps> = ({ restaurantId, className = '', iconOnly = false }) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const { isFavorite: checkFavorite, toggleFavorite } = useFavorites();
  
  const isFavorite = checkFavorite(restaurantId);

  let buttonTitle = 'Log in to save favorites';
  if (isAuthenticated) {
    buttonTitle = isFavorite ? 'Remove from favorites' : 'Add to favorites';
  }

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    try {
      await toggleFavorite(restaurantId);
    } catch (err) {
      console.error('Failed to toggle favorite', err);
    }
  };

  if (iconOnly) {
    return (
      <button
        type="button"
        className={`group p-2 rounded-full focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-colors shadow-sm ${
          isFavorite ? 'bg-primary text-surface hover:bg-primary-hover shadow-md' : 'bg-surface/80 text-text-secondary hover:bg-surface hover:text-primary backdrop-blur-sm'
        } ${className}`}
        onClick={handleClick}
        aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        title={buttonTitle}
      >
        <HeartIcon filled={isFavorite} />
      </button>
    );
  }

  return (
    <Button
      type="button"
      variant={isFavorite ? 'secondary' : 'outline'}
      size="sm"
      className={className}
      leftIcon={<HeartIcon filled={isFavorite} />}
      onClick={handleClick}
      aria-label={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
      title={buttonTitle}
    >
      {isFavorite ? 'Saved' : 'Save'}
    </Button>
  );
};

export default FavoriteButton;
