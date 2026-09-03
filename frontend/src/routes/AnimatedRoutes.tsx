import React, { useState, useEffect, useRef } from 'react';
import { useLocation, Routes, Route } from 'react-router-dom';
import gsap from 'gsap';
import MainLayout from '../layouts/MainLayout';
import Home from '../pages/Home';
import Login from '../pages/Login';
import Register from '../pages/Register';
import VerifyEmail from '../pages/VerifyEmail';
import NotFound from '../pages/NotFound';
import OrderHistory from '../pages/OrderHistory';
import OrderDetails from '../pages/OrderDetails';
import Profile from '../pages/Profile';
import RestaurantDetails from '../pages/RestaurantDetails';
import Checkout from '../pages/Checkout';
import IndexRoute from './IndexRoute';
import ProtectedRoute from './ProtectedRoute';

const AnimatedRoutes: React.FC = () => {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const transitionRef = useRef<HTMLDivElement>(null);
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (location.pathname !== displayLocation.pathname) {
      gsap.to(transitionRef.current, {
        opacity: 0,
        y: -15,
        duration: 0.25,
        ease: 'power2.inOut',
        onComplete: () => {
          // Once faded out, update the route
          setDisplayLocation(location);
          // Scroll to top instantly before fading in
          window.scrollTo(0, 0);
          // Fade in the new route
          gsap.fromTo(transitionRef.current,
            { opacity: 0, y: 15 },
            { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
          );
        }
      });
    }
  }, [location, displayLocation]);

  return (
    <div ref={transitionRef} className="flex flex-col min-h-screen">
      <Routes location={displayLocation}>
        <Route element={<MainLayout />}>
          {/* Public Routes */}
          <Route path="/" element={<IndexRoute />} />
          <Route path="/restaurants" element={<Home />} />
          <Route path="/restaurants/:restaurantId" element={<RestaurantDetails />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/verify-email" element={<VerifyEmail />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/profile" element={<Profile />} />
            <Route path="/orders" element={<OrderHistory />} />
            <Route path="/orders/:orderId" element={<OrderDetails />} />
            <Route path="/checkout" element={<Checkout />} />
          </Route>

          {/* Fallback Route */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </div>
  );
};

export default AnimatedRoutes;
