import os

base_dir = r"E:\project\shopconnect\frontend\src"

os.makedirs(os.path.join(base_dir, "layouts"), exist_ok=True)

# 1. MainLayout.jsx
main_layout_code = """import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';

const MainLayout = () => {
  return (
    <div className="min-h-screen bg-bg text-text font-sans flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
"""

# 2. SellerLayout.jsx
seller_layout_code = """import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const SellerLayout = () => {
  const { logout } = useAuth();
  const location = useLocation();

  const navLinks = [
    { name: 'Tableau de bord', path: '/seller' },
    { name: 'Mes Produits', path: '/seller/products' },
    { name: 'Commandes', path: '/seller/orders' },
    { name: 'Analyses', path: '/seller/analytics' },
    { name: 'Paramètres', path: '/seller/settings' },
  ];

  return (
    <div className="min-h-screen bg-bg text-text font-sans flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-border flex flex-col hidden md:flex">
        <div className="p-6 border-b border-border">
          <Link to="/" className="text-xl font-extrabold text-primary">ShopConnect Seller</Link>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.path}
              className={`block px-4 py-3 rounded-lg font-medium transition-colors ${
                location.pathname === link.path 
                  ? 'bg-primary/10 text-primary' 
                  : 'text-muted hover:bg-bg hover:text-text'
              }`}
            >
              {link.name}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-border">
          <button 
            onClick={logout}
            className="w-full text-left px-4 py-2 text-error hover:bg-error/10 rounded-lg font-medium transition-colors"
          >
            Déconnexion
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-x-hidden flex flex-col">
        {/* Mobile Header */}
        <header className="md:hidden bg-white border-b border-border p-4 flex justify-between items-center">
            <span className="font-extrabold text-primary">ShopConnect Seller</span>
            <button onClick={logout} className="text-error text-sm font-medium">Déconnexion</button>
        </header>
        <div className="p-4 md:p-8 flex-1">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default SellerLayout;
"""

# 3. AdminLayout.jsx
admin_layout_code = """import React from 'react';
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
"""

# 4. App.jsx
app_code = """import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import ProtectedRoute from './components/ProtectedRoute';

import MainLayout from './layouts/MainLayout';
import SellerLayout from './layouts/SellerLayout';
import AdminLayout from './layouts/AdminLayout';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Configure TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Temporary Placeholder Components
const Placeholder = ({ title }) => (
    <div className="flex justify-center items-center h-full min-h-[50vh]">
        <h1 className="text-3xl font-bold text-muted">{title}</h1>
    </div>
);

// Stubbing out required placeholder components
const HomePage = () => <Placeholder title="Home Page" />;
const ProductDetailPage = () => <Placeholder title="Product Detail" />;
const CartPage = () => <Placeholder title="Shopping Cart" />;
const CheckoutPage = () => <Placeholder title="Checkout" />;
const OrderHistoryPage = () => <Placeholder title="Order History" />;
const OrderDetailPage = () => <Placeholder title="Order Detail" />;
const ProfilePage = () => <Placeholder title="Profile" />;

const DashboardPage = () => <Placeholder title="Seller Dashboard" />;
const ProductsPage = () => <Placeholder title="My Products" />;
const OrdersPage = () => <Placeholder title="Manage Orders" />;
const ShopSettingsPage = () => <Placeholder title="Shop Settings" />;
const AnalyticsPage = () => <Placeholder title="Shop Analytics" />;

const AdminDashboardPage = () => <Placeholder title="Admin Dashboard" />;
const AdminUsersPage = () => <Placeholder title="Manage Users" />;
const AdminShopsPage = () => <Placeholder title="Manage Shops" />;

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CartProvider>
          <Router>
            <Routes>
              {/* Public layout */}
              <Route element={<MainLayout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/products/:id" element={<ProductDetailPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                {/* Protected customer routes */}
                <Route element={<ProtectedRoute />}>
                  <Route path="/cart" element={<CartPage />} />
                  <Route path="/checkout" element={<CheckoutPage />} />
                  <Route path="/orders" element={<OrderHistoryPage />} />
                  <Route path="/orders/:id" element={<OrderDetailPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Route>
              </Route>

              {/* Seller layout */}
              <Route element={<ProtectedRoute roles={['seller']} />}>
                <Route element={<SellerLayout />}>
                  <Route path="/seller" element={<DashboardPage />} />
                  <Route path="/seller/products" element={<ProductsPage />} />
                  <Route path="/seller/orders" element={<OrdersPage />} />
                  <Route path="/seller/settings" element={<ShopSettingsPage />} />
                  <Route path="/seller/analytics" element={<AnalyticsPage />} />
                </Route>
              </Route>

              {/* Admin layout */}
              <Route element={<ProtectedRoute roles={['admin', 'staff']} />}>
                <Route element={<AdminLayout />}>
                  <Route path="/admin" element={<AdminDashboardPage />} />
                  <Route path="/admin/users" element={<AdminUsersPage />} />
                  <Route path="/admin/shops" element={<AdminShopsPage />} />
                </Route>
              </Route>
            </Routes>
          </Router>
        </CartProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
"""

files = {
    os.path.join(base_dir, "layouts", "MainLayout.jsx"): main_layout_code,
    os.path.join(base_dir, "layouts", "SellerLayout.jsx"): seller_layout_code,
    os.path.join(base_dir, "layouts", "AdminLayout.jsx"): admin_layout_code,
    os.path.join(base_dir, "App.jsx"): app_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Layouts refactored successfully.")
