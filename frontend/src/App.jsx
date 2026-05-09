import React from 'react';
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
import HomePage from './pages/HomePage';

// Configure TanStack Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5, // 5 minutes fresh
      gcTime: 1000 * 60 * 10,   // 10 minutes cache
    },
  },
});

import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import OrderDetailPage from './pages/OrderDetailPage';
import OrderHistoryPage from './pages/OrderHistoryPage';
import SellerDashboardPage from './pages/SellerDashboardPage';
import SellerProductsPage from './pages/SellerProductsPage';
import SellerProductFormPage from './pages/SellerProductFormPage';
import SellerOrdersPage from './pages/SellerOrdersPage';

// Temporary Placeholder Components
const Placeholder = ({ title }) => (
    <div className="flex justify-center items-center h-full min-h-[50vh]">
        <h1 className="text-3xl font-bold text-muted">{title}</h1>
    </div>
);

// Stubbing out required placeholder components
const ProfilePage = () => <Placeholder title="Profile" />;

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
                  <Route path="/seller" element={<SellerDashboardPage />} />
                  <Route path="/seller/products" element={<SellerProductsPage />} />
                  <Route path="/seller/products/new" element={<SellerProductFormPage />} />
                  <Route path="/seller/products/:id/edit" element={<SellerProductFormPage />} />
                  <Route path="/seller/orders" element={<SellerOrdersPage />} />
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
