import type { FC } from 'react';
import { Link } from 'react-router-dom';

export const Footer: FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-border-default bg-background text-text-primary">
      <div className="container-page py-16">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4 lg:gap-12">
          {/* Brand & Description */}
          <div className="space-y-6 md:col-span-1">
            <Link
              to="/"
              className="inline-block text-3xl font-bold tracking-tight transition-base hover:opacity-80"
            >
              <span>Bite<span className="font-serif italic font-normal tracking-normal">Up.</span></span>
            </Link>
            <p className="text-sm leading-relaxed text-text-secondary">
              Curated local tastes, delivered with precision. Elevating the standard for modern food discovery.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="mb-6 text-xs font-semibold tracking-wider text-text-primary uppercase">
              Explore
            </h4>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li>
                <Link to="/" className="transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Restaurants
                </Link>
              </li>
              <li>
                <Link to="/orders" className="transition-base hover:text-text-primary hover:underline underline-offset-4">
                  My Orders
                </Link>
              </li>
              <li>
                <Link to="/profile" className="transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Account Profile
                </Link>
              </li>
            </ul>
          </div>

          {/* Partners & Delivery */}
          <div>
            <h4 className="mb-6 text-xs font-semibold tracking-wider text-text-primary uppercase">
              Partners
            </h4>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li>
                <span className="cursor-pointer transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Add Your Restaurant
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Deliver with BiteUp
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Business Accounts
                </span>
              </li>
            </ul>
          </div>

          {/* Help & Support */}
          <div>
            <h4 className="mb-6 text-xs font-semibold tracking-wider text-text-primary uppercase">
              Support
            </h4>
            <ul className="space-y-3 text-sm text-text-secondary">
              <li>
                <span className="cursor-pointer transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Help Center
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Terms of Service
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-text-primary hover:underline underline-offset-4">
                  Privacy Policy
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-16 border-t border-border-default pt-8 text-center text-xs text-text-muted sm:flex sm:items-center sm:justify-between sm:text-left">
          <p>&copy; {currentYear} BiteUp Technologies Inc. All rights reserved.</p>
          <p className="mt-2 sm:mt-0 font-serif italic text-sm">Crafted with intentionality.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
