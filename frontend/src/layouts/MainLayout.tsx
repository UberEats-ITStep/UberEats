import type { FC } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Navbar, Footer } from '../components/layout';
import CartDrawer from '../features/cart/components/CartDrawer';

const MainLayout: FC = () => {
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuth();
  
  // Hide Navbar on the root page if the user is unauthenticated
  // since the EditorialHero provides its own top navigation.
  const showNavbar = !(location.pathname === '/' && !isAuthenticated && !isLoading);

  // Hide the footer on authentication pages to maintain a clean, focused user experience.
  const isAuthPage = ['/login', '/register', '/verify-email'].includes(location.pathname);

  return (
    <div className="flex min-h-screen flex-col bg-background font-sans text-text-primary">
      {showNavbar && <Navbar />}
      <CartDrawer />
      <main className="flex-1 flex flex-col">
        <Outlet />
      </main>
      {!isAuthPage && <Footer />}
    </div>
  );
};

export default MainLayout;
