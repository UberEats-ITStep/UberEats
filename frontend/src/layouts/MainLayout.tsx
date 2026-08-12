import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar, Footer } from '../components/layout';
import CartDrawer from '../features/cart/components/CartDrawer';

const MainLayout: FC = () => {
  return (
    <div className="flex min-h-screen flex-col bg-background font-sans text-text-primary">
      <Navbar />
      <CartDrawer />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout;
