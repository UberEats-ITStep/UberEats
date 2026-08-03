import { useState, type ChangeEvent } from 'react';
import type { FC } from 'react';
import { Link, useLocation, useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useCart } from '../../context/CartContext';
import Button from '../common/Button';
import Input from '../common/Input';

export const Navbar: FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const { itemCount, setIsDrawerOpen } = useCart();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const searchQuery = searchParams.get('q') || '';

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

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value) {
      setSearchParams({ q: value });
      // If we are not on home, redirect to home with search
      if (location.pathname !== '/' && location.pathname !== '/restaurants') {
         navigate(`/?q=${encodeURIComponent(value)}`);
      }
    } else {
      searchParams.delete('q');
      setSearchParams(searchParams);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-primary text-text-inverse shadow-elevated">
      <div className="container-page">
        <nav className="flex h-16 items-center justify-between gap-4 md:gap-8">
          {/* Brand Logo & Links */}
          <div className="flex items-center gap-8 shrink-0">
            <Link
              to="/"
              onClick={closeMenu}
              className="flex items-center gap-2 text-2xl font-extrabold tracking-tight text-white transition-base hover:opacity-90"
            >
              <span>Bite<span className="text-accent">Up</span></span>
            </Link>

            {/* Desktop Nav Links */}
            <div className="hidden lg:flex lg:items-center lg:gap-6">
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

          {/* Flexible Search Bar */}
          <div className="flex-1 max-w-2xl hidden sm:block">
             <Input
                type="search"
                placeholder="Search restaurants or cuisines..."
                aria-label="Search restaurants or cuisines"
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full bg-white/10 text-white placeholder-slate-300 border-transparent focus:bg-white focus:text-text-primary focus:border-accent"
                leftIcon={
                   <svg className="h-5 w-5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                   </svg>
                }
             />
          </div>

          {/* Desktop Right Actions */}
          <div className="hidden items-center gap-4 md:flex shrink-0">
            {isAuthenticated ? (
              <>
                <button
                  type="button"
                  onClick={() => setIsDrawerOpen(true)}
                  className="relative rounded-sm p-2 text-slate-200 hover:bg-primary-hover hover:text-white focus:outline-none focus:ring-2 focus:ring-accent"
                  aria-label="Open cart"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  {itemCount > 0 && (
                    <span className="absolute top-0 right-0 inline-flex items-center justify-center rounded-full bg-accent px-1.5 py-0.5 text-xs font-bold leading-none text-text-primary transform translate-x-1/4 -translate-y-1/4">
                      {itemCount}
                    </span>
                  )}
                </button>
                <Button
                  variant="ghost-inverse"
                  size="sm"
                  onClick={logout}
                >
                  Logout
                </Button>
              </>
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

          {/* Mobile Menu Button & Cart */}
          <div className="flex md:hidden items-center gap-2 shrink-0">
            {isAuthenticated && (
              <button
                type="button"
                onClick={() => setIsDrawerOpen(true)}
                className="relative rounded-sm p-2 text-slate-200 hover:bg-primary-hover hover:text-white focus:outline-none focus:ring-2 focus:ring-accent"
                aria-label="Open cart"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                {itemCount > 0 && (
                  <span className="absolute top-0 right-0 inline-flex items-center justify-center rounded-full bg-accent px-1.5 py-0.5 text-xs font-bold leading-none text-text-primary transform translate-x-1/4 -translate-y-1/4">
                    {itemCount}
                  </span>
                )}
              </button>
            )}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center rounded-sm p-2 text-slate-200 hover:bg-primary-hover hover:text-white focus:outline-none focus:ring-2 focus:ring-accent"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              <span className="sr-only">Open main menu</span>
              {mobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </nav>
        
        {/* Mobile Search Bar (visible only on very small screens < sm) */}
        <div className="sm:hidden pb-3">
           <Input
              type="search"
              placeholder="Search restaurants..."
              aria-label="Search restaurants"
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full bg-white/10 text-white placeholder-slate-300 border-transparent focus:bg-white focus:text-text-primary focus:border-accent"
              leftIcon={
                 <svg className="h-5 w-5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                 </svg>
              }
           />
        </div>
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
