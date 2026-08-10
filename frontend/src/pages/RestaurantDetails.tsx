import type { FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useRestaurantDetails } from '../features/restaurants/hooks/useRestaurantDetails';
import RestaurantHero from '../features/restaurants/components/RestaurantHero';
import RestaurantStats from '../features/restaurants/components/RestaurantStats';
import CategoryNavbar from '../features/restaurants/components/CategoryNavbar';
import MenuSection from '../features/restaurants/components/MenuSection';
import { LoadingState, Alert, Button, SectionContainer } from '../components/common';
import { useCart } from '../context/CartContext';
import type { MenuItem } from '../features/restaurants/types/restaurant.types';
import ReviewList from '../features/reviews/components/ReviewList';

const RestaurantDetails: FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const { restaurant, isLoading, error, reload } = useRestaurantDetails(restaurantId);
  const { addToCart } = useCart();

  const handleAddToCart = (item: MenuItem) => {
    if (restaurant) {
      void addToCart(item.id, 1, restaurant.id);
    }
  };

  if (isLoading) {
    return (
      <SectionContainer width="page" padding="lg">
        <LoadingState message="Loading restaurant and menu..." />
      </SectionContainer>
    );
  }

  if (error || !restaurant) {
    return (
      <SectionContainer width="content" padding="lg">
        <Alert
          variant="error"
          title="Restaurant unavailable"
          message={error || 'The requested restaurant could not be found.'}
          onRetry={reload}
          action={
            <Link to="/">
              <Button variant="outline" size="sm">
                Browse restaurants
              </Button>
            </Link>
          }
        />
      </SectionContainer>
    );
  }

  return (
    <SectionContainer width="page" padding="md" className="pb-16">
      <Link
        to="/"
        className="mb-5 inline-flex items-center font-button text-text-secondary transition-base hover:text-primary"
      >
        ← All restaurants
      </Link>

      <RestaurantHero restaurant={restaurant} />
      <RestaurantStats restaurant={restaurant} />

      <main className="mt-12">
        <div className="flex flex-col gap-5 border-b border-border-default pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-caption text-accent">Explore</p>
            <h2 className="mt-1 text-page-title">Our menu</h2>
          </div>
          <CategoryNavbar categories={restaurant.categories} />
        </div>

        <MenuSection categories={restaurant.categories} onAddToCart={handleAddToCart} />
        
        {/* Customer Reviews Section */}
        <div className="mt-16 border-t border-border-default">
          <ReviewList restaurant={restaurant} onReviewChange={() => reload(true)} />
        </div>
      </main>
    </SectionContainer>
  );
};

export default RestaurantDetails;
