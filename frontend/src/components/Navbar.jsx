import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { itemCount } = useCart();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-border sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Desktop Nav */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center gap-2 group">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center transform group-hover:rotate-12 transition-transform">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <span className="font-extrabold text-xl text-text tracking-tight">ShopConnect</span>
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              <Link to="/catalog" className="text-muted hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors">
                Catalogue
              </Link>
            </div>
          </div>

          {/* Desktop Right Side */}
          <div className="hidden sm:flex sm:items-center sm:space-x-4">
            <Link to="/cart" className="relative p-2 text-muted hover:text-primary transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {itemCount > 0 && (
                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-red-500 rounded-full">
                  {itemCount}
                </span>
              )}
            </Link>

            {user ? (
              <div className="flex items-center space-x-4 pl-4 border-l border-border">
                <span className="text-sm font-semibold text-text">
                  {user.first_name} {user.last_name}
                </span>
                <Link to="/orders" className="text-sm font-medium text-muted hover:text-primary transition-colors">
                  Mes Commandes
                </Link>
                {user.role === 'seller' && (
                  <Link to="/seller" className="text-sm font-bold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg hover:bg-emerald-100 transition-colors">
                    Tableau de bord Vendeur
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="text-sm font-medium text-error hover:text-error transition-colors bg-red-50 px-3 py-1.5 rounded-lg hover:bg-red-100"
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3 pl-4 border-l border-border">
                <Link to="/login" className="text-sm font-medium text-muted hover:text-primary px-3 py-2 rounded-lg transition-colors">
                  Connexion
                </Link>
                <Link to="/register" className="text-sm font-medium bg-primary text-white hover:bg-primary-dark px-4 py-2 rounded-lg transition-colors shadow-sm">
                  S'inscrire
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden space-x-2">
            <Link to="/cart" className="relative p-2 text-muted">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {itemCount > 0 && (
                <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-[10px] font-bold leading-none text-white transform translate-x-1/4 -translate-y-1/4 bg-red-500 rounded-full">
                  {itemCount}
                </span>
              )}
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-muted hover:text-muted hover:bg-border/50 focus:outline-none"
            >
              <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="sm:hidden border-t border-border bg-bg">
          <div className="pt-2 pb-3 space-y-1">
            <Link to="/catalog" className="block px-4 py-2 text-base font-medium text-text hover:text-primary hover:bg-border/50">
              Catalogue
            </Link>
          </div>
          <div className="pt-4 pb-3 border-t border-border">
            {user ? (
              <div className="px-4 space-y-3">
                <div>
                  <div className="text-base font-medium text-text">{user.first_name} {user.last_name}</div>
                  <div className="text-sm font-medium text-muted">{user.phone}</div>
                </div>
                <Link to="/orders" className="block px-3 py-2 text-base font-medium text-text hover:text-primary hover:bg-border/50 rounded-md">
                  Mes Commandes
                </Link>
                {user.role === 'seller' && (
                  <Link to="/seller" className="block px-3 py-2 text-base font-bold text-emerald-600 bg-emerald-50 hover:bg-emerald-100 rounded-md">
                    Tableau de bord Vendeur
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="w-full text-left block px-3 py-2 text-base font-medium text-error hover:bg-red-50 rounded-md"
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <div className="px-4 space-y-2">
                <Link to="/login" className="block w-full text-center px-4 py-2 border border-border rounded-md shadow-sm text-base font-medium text-text bg-white hover:bg-bg">
                  Connexion
                </Link>
                <Link to="/register" className="block w-full text-center px-4 py-2 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-primary hover:bg-primary-dark">
                  S'inscrire
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
