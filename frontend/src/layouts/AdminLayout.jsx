import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const AdminLayout = () => {
  const { logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { name: 'Dashboard', path: '/admin' },
    { name: 'Utilisateurs', path: '/admin/users' },
    { name: 'Boutiques', path: '/admin/shops' },
  ];

  return (
    <div className="min-h-screen bg-bg font-sans flex">
      {/* Dark Sidebar for Admin */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col hidden md:flex shadow-xl z-10">
        <div className="p-6 border-b border-slate-800">
          <Link to="/" className="text-xl font-extrabold text-white">ShopConnect Admin</Link>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              className={`block px-4 py-3 rounded-lg font-medium transition-colors ${
                location.pathname === link.path 
                  ? 'bg-primary text-white' 
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              {link.name}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-800">
          <button 
            onClick={logout}
            className="w-full text-left px-4 py-2 text-red-400 hover:bg-slate-800 rounded-lg font-medium transition-colors"
          >
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-x-hidden flex flex-col text-text">
        <header className="md:hidden bg-slate-900 text-white p-4 flex justify-between items-center">
            <span className="font-extrabold">SC Admin</span>
            <button onClick={logout} className="text-red-400 text-sm font-medium">Déconnexion</button>
        </header>
        <div className="p-4 md:p-8 flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
