import os

base_dir = r"E:\project\shopconnect\frontend\src"

# Make sure directories exist
os.makedirs(os.path.join(base_dir, "services"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "context"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "components"), exist_ok=True)

api_code = """import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

// Request interceptor: attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: auto-refresh token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 Unauthorized and we haven't already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error("No refresh token available");
        }
        
        // Call refresh endpoint outside of the `api` instance to prevent loops
        const { data } = await axios.post(`${import.meta.env.VITE_API_URL}/auth/token/refresh/`, {
          refresh: refreshToken
        });
        
        // Backend returns success wrapper
        const newAccess = data?.data?.access;
        if (newAccess) {
            localStorage.setItem('access_token', newAccess);
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            return api(originalRequest);
        } else {
            throw new Error("Invalid token refresh payload");
        }
      } catch (err) {
        // Refresh failed (token expired or invalid)
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(err);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
"""

auth_context_code = """import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const loadUser = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const { data } = await api.get('/auth/me/');
            if (data.success) {
                setUser(data.data);
            }
        } catch (error) {
            console.error("Failed to load user session", error);
            // 401s are caught by api interceptor which auto-clears and redirects
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUser();
    }, []);

    const login = async (phone, password) => {
        const { data } = await api.post('/auth/login/', { phone, password });
        if (data.success) {
            localStorage.setItem('access_token', data.data.tokens.access);
            localStorage.setItem('refresh_token', data.data.tokens.refresh);
            setUser(data.data.user);
            return data.data;
        }
        return null;
    };

    const register = async (userData) => {
        const { data } = await api.post('/auth/register/', userData);
        if (data.success) {
            localStorage.setItem('access_token', data.data.tokens.access);
            localStorage.setItem('refresh_token', data.data.tokens.refresh);
            setUser(data.data.user);
            return data.data;
        }
        return null;
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout, loadUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
"""

cart_context_code = """import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();

    const fetchCart = async () => {
        if (!user) {
            setItems([]);
            setLoading(false);
            return;
        }
        try {
            const { data } = await api.get('/cart/');
            if (data.success) {
                setItems(data.data);
            }
        } catch (error) {
            console.error("Failed to fetch cart", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, [user]);

    const addItem = async (productId, quantity = 1, variantId = null) => {
        try {
            const { data } = await api.post('/cart/add/', { 
                product_id: productId, 
                quantity, 
                variant_id: variantId 
            });
            if (data.success) {
                await fetchCart(); // Refresh to get fully populated nested data
                return data.data;
            }
        } catch (error) {
            throw error.response?.data?.error || error;
        }
    };

    const updateItem = async (itemId, quantity) => {
        try {
            const { data } = await api.put(`/cart/update/${itemId}/`, { quantity });
            if (data.success) {
                await fetchCart();
                return data.data;
            }
        } catch (error) {
            throw error.response?.data?.error || error;
        }
    };

    const removeItem = async (itemId) => {
        try {
            const { data } = await api.delete(`/cart/remove/${itemId}/`);
            if (data.success) {
                setItems(prev => prev.filter(item => item.id !== itemId));
            }
        } catch (error) {
            throw error.response?.data?.error || error;
        }
    };

    const clearCart = () => {
        setItems([]);
    };

    // Calculate derived state
    const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
    
    const total = items.reduce((sum, item) => {
        if (!item.product_details) return sum;
        
        let price = parseFloat(item.product_details.discount_price || item.product_details.price);
        
        // Add variant price if applicable
        if (item.variant && item.product_details.variants) {
            const variantObj = item.product_details.variants.find(v => v.id === item.variant);
            if (variantObj) {
                price += parseFloat(variantObj.additional_price || 0);
            }
        }
        
        return sum + (price * item.quantity);
    }, 0);

    return (
        <CartContext.Provider value={{ 
            items, loading, itemCount, total, 
            addItem, updateItem, removeItem, clearCart, fetchCart 
        }}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => useContext(CartContext);
"""

protected_route_code = """import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ roles = [] }) => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen bg-slate-50">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (roles.length > 0 && !roles.includes(user.role)) {
        // Redirect to home if they don't have the right role
        return <Navigate to="/" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
"""

app_code = """import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import ProtectedRoute from './components/ProtectedRoute';

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
    <div className="flex justify-center items-center h-[calc(100vh-4rem)]">
        <h1 className="text-3xl font-bold text-slate-400">{title}</h1>
    </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CartProvider>
          <Router>
            <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
              {/* Future Navbar Position */}
              
              <main>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<Placeholder title="Home Page" />} />
                  <Route path="/login" element={<Placeholder title="Login Page" />} />
                  <Route path="/register" element={<Placeholder title="Register Page" />} />
                  <Route path="/catalog" element={<Placeholder title="Catalog List" />} />
                  <Route path="/catalog/:id" element={<Placeholder title="Product Detail" />} />
                  
                  {/* Protected Routes (Customer) */}
                  <Route element={<ProtectedRoute />}>
                    <Route path="/cart" element={<Placeholder title="Shopping Cart" />} />
                    <Route path="/checkout" element={<Placeholder title="Checkout" />} />
                    <Route path="/orders" element={<Placeholder title="My Orders" />} />
                  </Route>

                  {/* Protected Routes (Seller) */}
                  <Route element={<ProtectedRoute roles={['seller']} />}>
                    <Route path="/seller" element={<Placeholder title="Seller Dashboard" />} />
                  </Route>

                  {/* Protected Routes (Driver) */}
                  <Route element={<ProtectedRoute roles={['driver']} />}>
                    <Route path="/driver" element={<Placeholder title="Driver Dashboard" />} />
                  </Route>
                </Routes>
              </main>
            </div>
          </Router>
        </CartProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
"""

# Files creation
files = {
    os.path.join(base_dir, "services", "api.js"): api_code,
    os.path.join(base_dir, "context", "AuthContext.jsx"): auth_context_code,
    os.path.join(base_dir, "context", "CartContext.jsx"): cart_context_code,
    os.path.join(base_dir, "components", "ProtectedRoute.jsx"): protected_route_code,
    os.path.join(base_dir, "App.jsx"): app_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("React Foundation created.")
