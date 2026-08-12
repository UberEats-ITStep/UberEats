import type { FC } from 'react';
import { Link } from 'react-router-dom';

export const Footer: FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-primary-hover bg-primary text-text-inverse">
      <div className="container-page py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4 lg:gap-12">
          {/* Brand & Description */}
          <div className="space-y-4 md:col-span-1">
            <Link
              to="/"
              className="inline-block text-2xl font-extrabold tracking-tight text-white transition-base hover:opacity-90"
            >
              <span>Bite<span className="text-accent">Up</span></span>
            </Link>
            <p className="text-sm leading-relaxed text-slate-300">
              Discover and order from the best local restaurants around you. Fresh food delivered fast to your doorstep.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="mb-4 text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Explore
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>
                <Link to="/" className="transition-base hover:text-white hover:underline">
                  Restaurants
                </Link>
              </li>
              <li>
                <Link to="/orders" className="transition-base hover:text-white hover:underline">
                  My Orders
                </Link>
              </li>
              <li>
                <Link to="/profile" className="transition-base hover:text-white hover:underline">
                  Account Profile
                </Link>
              </li>
            </ul>
          </div>

          {/* Partners & Delivery */}
          <div>
            <h4 className="mb-4 text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Partners
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>
                <span className="cursor-pointer transition-base hover:text-white hover:underline">
                  Add Your Restaurant
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-white hover:underline">
                  Deliver with BiteUp
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-white hover:underline">
                  Business Accounts
                </span>
              </li>
            </ul>
          </div>

          {/* Help & Support */}
          <div>
            <h4 className="mb-4 text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Support
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li>
                <span className="cursor-pointer transition-base hover:text-white hover:underline">
                  Help Center
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-white hover:underline">
                  Terms of Service
                </span>
              </li>
              <li>
                <span className="cursor-pointer transition-base hover:text-white hover:underline">
                  Privacy Policy
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-primary-hover pt-8 text-center text-xs text-slate-400 sm:flex sm:items-center sm:justify-between sm:text-left">
          <p>&copy; {currentYear} BiteUp Technologies Inc. All rights reserved.</p>
          <p className="mt-2 sm:mt-0">Designed with a modern semantic token system.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
