import { useMemo, useState, type FC } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useRestaurantDetails } from '../features/restaurants/hooks/useRestaurantDetails';
import RestaurantHero from '../features/restaurants/components/RestaurantHero';
import RestaurantStats from '../features/restaurants/components/RestaurantStats';
import CategoryNavbar from '../features/restaurants/components/CategoryNavbar';
import MenuSection from '../features/restaurants/components/MenuSection';
import MenuFilters from '../features/restaurants/components/MenuFilters';
import { LoadingState, Alert, Button, SectionContainer } from '../components/common';
import { useCart } from '../context/CartContext';
import type { MenuItem } from '../features/restaurants/types/restaurant.types';
import ReviewList from '../features/reviews/components/ReviewList';
import { filterMenuCategories } from '../features/restaurants/utils/menuFiltering';

const RestaurantDetails: FC = () => {
  const { restaurantId } = useParams<{ restaurantId: string }>();
  const { restaurant, isLoading, error, reload } = useRestaurantDetails(restaurantId);
  const { addToCart, isLoading: isCartLoading } = useCart();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | 'all'>('all');
  const [showAvailableOnly, setShowAvailableOnly] = useState(false);

  const filteredCategories = useMemo(() => {
    if (!restaurant) {
      return [];
    }

    return filterMenuCategories(restaurant.categories, {
      searchTerm,
      selectedCategory,
      showAvailableOnly,
    });
  }, [restaurant, searchTerm, selectedCategory, showAvailableOnly]);

  const handleAddToCart = (item: MenuItem) => {
    if (restaurant) {
      void addToCart(item.id, 1, restaurant.id);
    }
  };

  const clearMenuFilters = () => {
    setSearchTerm('');
    setSelectedCategory('all');
    setShowAvailableOnly(false);
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
    <div className="bg-background min-h-screen">
      <SectionContainer width="page" padding="md" className="pb-16 pt-6">
        <Link
          to="/"
          className="mb-8 inline-flex items-center text-sm font-medium tracking-widest uppercase text-text-muted transition-base hover:text-text-primary underline underline-offset-4"
        >
          ← Directory
        </Link>

        <RestaurantHero restaurant={restaurant} />
        <RestaurantStats restaurant={restaurant} />

        <main className="mt-16">
          <div className="flex flex-col gap-6 border-b border-text-primary pb-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs tracking-widest uppercase text-text-muted mb-2">Explore</p>
              <h2 className="text-5xl font-serif italic text-text-primary">The Menu</h2>
            </div>
            <div className="lg:w-1/2">
              <CategoryNavbar categories={filteredCategories} />
            </div>
          </div>

          <div className="mt-8">
            <MenuFilters
              categories={restaurant.categories}
              searchTerm={searchTerm}
              selectedCategory={selectedCategory}
              showAvailableOnly={showAvailableOnly}
              onSearchChange={setSearchTerm}
              onCategoryChange={setSelectedCategory}
              onAvailabilityToggle={setShowAvailableOnly}
              onClear={clearMenuFilters}
            />
          </div>

          <MenuSection categories={filteredCategories} onAddToCart={handleAddToCart} isLoading={isCartLoading} />

          <div className="mt-24 border-t border-text-primary pt-8">
            <ReviewList restaurant={restaurant} onReviewChange={() => reload(true)} />
          </div>
        </main>
      </SectionContainer>
    </div>
  );
};

export default RestaurantDetails;
