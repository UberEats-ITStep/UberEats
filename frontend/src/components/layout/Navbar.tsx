import { useState } from 'react';
import type { FC } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../common/Button';

export const Navbar: FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const closeMenu = () => setMobileMenuOpen(false);

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/restaurants';
    }
    return location.pathname === path;
  };

  const navLinkClass = (path: string) =>
    `text-sm font-medium transition-base py-2 px-1 border-b-2 ${
      isActive(path)
        ? 'border-accent text-accent font-semibold'
        : 'border-transparent text-slate-200 hover:text-white hover:border-slate-400'
    }`;

  const mobileNavLinkClass = (path: string) =>
    `block py-2.5 px-4 rounded-md text-base font-medium transition-base ${
      isActive(path)
        ? 'bg-primary-hover text-accent font-semibold'
        : 'text-slate-200 hover:bg-primary-hover hover:text-white'
    }`;

  return (
    <header className="sticky top-0 z-50 bg-primary text-text-inverse shadow-elevated">
      <div className="container-page">
        <nav className="flex h-16 items-center justify-between">
          {/* Brand Logo */}
          <div className="flex items-center gap-8">
            <Link
              to="/"
              onClick={closeMenu}
              className="flex items-center gap-2 text-2xl font-extrabold tracking-tight text-white transition-base hover:opacity-90"
            >
              <span>Bite<span className="text-accent">Up</span></span>
            </Link>

            {/* Desktop Nav Links */}
            <div className="hidden md:flex md:items-center md:gap-6">
              <Link to="/" className={navLinkClass('/')}>
                Restaurants
              </Link>
              {isAuthenticated && (
                <>
                  <Link to="/orders" className={navLinkClass('/orders')}>
                    Orders
                  </Link>
                  <Link to="/profile" className={navLinkClass('/profile')}>
                    Profile
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Desktop Right Actions */}
          <div className="hidden items-center gap-4 md:flex">
            {isAuthenticated ? (
              <Button
                variant="ghost-inverse"
                size="sm"
                onClick={logout}
              >
                Logout
              </Button>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login">
                  <Button
                    variant="ghost-inverse"
                    size="sm"
                  >
                    Log in
                  </Button>
                </Link>
                <Link to="/register">
                  <Button variant="accent" size="sm">
                    Sign up
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center rounded-sm p-2 text-slate-200 hover:bg-primary-hover hover:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="2"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="2"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </nav>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="border-t border-primary-hover bg-primary px-4 pt-2 pb-6 md:hidden">
          <div className="space-y-1">
            <Link to="/" onClick={closeMenu} className={mobileNavLinkClass('/')}>
              Restaurants
            </Link>
            {isAuthenticated ? (
              <>
                <Link to="/orders" onClick={closeMenu} className={mobileNavLinkClass('/orders')}>
                  Orders
                </Link>
                <Link to="/profile" onClick={closeMenu} className={mobileNavLinkClass('/profile')}>
                  Profile
                </Link>
                <div className="pt-4">
                  <Button
                    variant="ghost-inverse"
                    fullWidth
                    onClick={() => {
                      closeMenu();
                      logout();
                    }}
                    className="justify-start text-status-error hover:bg-primary-hover hover:text-red-400"
                  >
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <div className="space-y-3 pt-4">
                <Link to="/login" onClick={closeMenu} className="block">
                  <Button
                    variant="outline-inverse"
                    fullWidth
                    className="justify-center"
                  >
                    Log in
                  </Button>
                </Link>
                <Link to="/register" onClick={closeMenu} className="block">
                  <Button variant="accent" fullWidth className="justify-center font-bold">
                    Sign up
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
