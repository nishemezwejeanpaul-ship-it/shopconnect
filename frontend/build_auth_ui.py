import os

base_dir = r"E:\project\shopconnect\frontend\src"

os.makedirs(os.path.join(base_dir, "pages"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "components"), exist_ok=True)

login_page_code = """import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const loginSchema = z.object({
  phone: z.string().min(1, 'Le numéro de téléphone est requis'),
  password: z.string().min(1, 'Le mot de passe est requis'),
});

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data) => {
    setErrorMsg('');
    setIsSubmitting(true);
    try {
      const result = await login(data.phone, data.password);
      if (result) {
        navigate('/');
      } else {
        setErrorMsg("Numéro de téléphone ou mot de passe incorrect.");
      }
    } catch (err) {
      setErrorMsg(err?.response?.data?.error?.message || "Une erreur inattendue s'est produite.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gradient-to-br from-slate-50 to-indigo-50 p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-slate-100 transition-all duration-300 hover:shadow-2xl">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-slate-900 mb-2">Bienvenue</h2>
          <p className="text-slate-500">Connectez-vous à votre compte ShopConnect</p>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Numéro de téléphone</label>
            <input
              type="text"
              {...register('phone')}
              placeholder="Ex: +257..."
              className={`w-full px-4 py-3 rounded-xl border ${errors.phone ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors`}
            />
            {errors.phone && <p className="mt-2 text-sm text-red-500">{errors.phone.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Mot de passe</label>
            <input
              type="password"
              {...register('password')}
              placeholder="••••••••"
              className={`w-full px-4 py-3 rounded-xl border ${errors.password ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors`}
            />
            {errors.password && <p className="mt-2 text-sm text-red-500">{errors.password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-xl transition-all duration-200 flex justify-center items-center disabled:opacity-70 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
          >
            {isSubmitting ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-slate-600 text-sm">
            Vous n'avez pas de compte ?{' '}
            <Link to="/register" className="text-indigo-600 font-bold hover:text-indigo-800 transition-colors">
              Créer un compte
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
"""

register_page_code = """import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const registerSchema = z.object({
  first_name: z.string().min(1, 'Le prénom est requis'),
  last_name: z.string().min(1, 'Le nom est requis'),
  phone: z.string().min(1, 'Le numéro de téléphone est requis'),
  password: z.string().min(8, 'Le mot de passe doit contenir au moins 8 caractères'),
  confirm_password: z.string()
}).refine((data) => data.password === data.confirm_password, {
  message: "Les mots de passe ne correspondent pas",
  path: ["confirm_password"]
});

const RegisterPage = () => {
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema)
  });

  const onSubmit = async (data) => {
    setErrorMsg('');
    setIsSubmitting(true);
    try {
      const payload = {
        first_name: data.first_name,
        last_name: data.last_name,
        phone: data.phone,
        password: data.password
      };
      const result = await registerUser(payload);
      if (result) {
        navigate('/');
      } else {
        setErrorMsg("Erreur lors de l'inscription.");
      }
    } catch (err) {
      setErrorMsg(err?.response?.data?.error?.message || "Une erreur inattendue s'est produite.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gradient-to-tr from-slate-50 to-blue-50 p-4 py-12">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-slate-100 transition-all duration-300 hover:shadow-2xl">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-slate-900 mb-2">Rejoignez-nous</h2>
          <p className="text-slate-500">Créez votre compte ShopConnect</p>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Prénom</label>
              <input
                type="text"
                {...register('first_name')}
                className={`w-full px-4 py-3 rounded-xl border ${errors.first_name ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
              {errors.first_name && <p className="mt-2 text-xs text-red-500">{errors.first_name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Nom</label>
              <input
                type="text"
                {...register('last_name')}
                className={`w-full px-4 py-3 rounded-xl border ${errors.last_name ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
              {errors.last_name && <p className="mt-2 text-xs text-red-500">{errors.last_name.message}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Numéro de téléphone</label>
            <input
              type="text"
              {...register('phone')}
              placeholder="Ex: +257..."
              className={`w-full px-4 py-3 rounded-xl border ${errors.phone ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.phone && <p className="mt-2 text-xs text-red-500">{errors.phone.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Mot de passe</label>
            <input
              type="password"
              {...register('password')}
              placeholder="••••••••"
              className={`w-full px-4 py-3 rounded-xl border ${errors.password ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.password && <p className="mt-2 text-xs text-red-500">{errors.password.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Confirmer le mot de passe</label>
            <input
              type="password"
              {...register('confirm_password')}
              placeholder="••••••••"
              className={`w-full px-4 py-3 rounded-xl border ${errors.confirm_password ? 'border-red-500 bg-red-50' : 'border-slate-200 bg-slate-50'} focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.confirm_password && <p className="mt-2 text-xs text-red-500">{errors.confirm_password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl transition-all duration-200 flex justify-center items-center mt-4 shadow-md hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              "S'inscrire"
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-slate-600 text-sm">
            Vous avez déjà un compte ?{' '}
            <Link to="/login" className="text-blue-600 font-bold hover:text-blue-800 transition-colors">
              Se connecter
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
"""

navbar_code = """import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { itemCount } = useCart();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Desktop Nav */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center gap-2 group">
              <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center transform group-hover:rotate-12 transition-transform">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <span className="font-extrabold text-xl text-slate-900 tracking-tight">ShopConnect</span>
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
              <Link to="/catalog" className="text-slate-600 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
                Catalogue
              </Link>
            </div>
          </div>

          {/* Desktop Right Side */}
          <div className="hidden sm:flex sm:items-center sm:space-x-4">
            <Link to="/cart" className="relative p-2 text-slate-500 hover:text-indigo-600 transition-colors">
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
              <div className="flex items-center space-x-4 pl-4 border-l border-slate-200">
                <span className="text-sm font-semibold text-slate-700">
                  {user.first_name} {user.last_name}
                </span>
                <button
                  onClick={logout}
                  className="text-sm font-medium text-red-600 hover:text-red-800 transition-colors bg-red-50 px-3 py-1.5 rounded-lg hover:bg-red-100"
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3 pl-4 border-l border-slate-200">
                <Link to="/login" className="text-sm font-medium text-slate-600 hover:text-indigo-600 px-3 py-2 rounded-lg transition-colors">
                  Connexion
                </Link>
                <Link to="/register" className="text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 px-4 py-2 rounded-lg transition-colors shadow-sm">
                  S'inscrire
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden space-x-2">
            <Link to="/cart" className="relative p-2 text-slate-500">
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
              className="inline-flex items-center justify-center p-2 rounded-md text-slate-400 hover:text-slate-500 hover:bg-slate-100 focus:outline-none"
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
        <div className="sm:hidden border-t border-slate-200 bg-slate-50">
          <div className="pt-2 pb-3 space-y-1">
            <Link to="/catalog" className="block px-4 py-2 text-base font-medium text-slate-700 hover:text-indigo-600 hover:bg-slate-100">
              Catalogue
            </Link>
          </div>
          <div className="pt-4 pb-3 border-t border-slate-200">
            {user ? (
              <div className="px-4 space-y-3">
                <div>
                  <div className="text-base font-medium text-slate-800">{user.first_name} {user.last_name}</div>
                  <div className="text-sm font-medium text-slate-500">{user.phone}</div>
                </div>
                <button
                  onClick={logout}
                  className="w-full text-left block px-3 py-2 text-base font-medium text-red-600 hover:bg-red-50 rounded-md"
                >
                  Déconnexion
                </button>
              </div>
            ) : (
              <div className="px-4 space-y-2">
                <Link to="/login" className="block w-full text-center px-4 py-2 border border-slate-300 rounded-md shadow-sm text-base font-medium text-slate-700 bg-white hover:bg-slate-50">
                  Connexion
                </Link>
                <Link to="/register" className="block w-full text-center px-4 py-2 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700">
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
"""

app_update_code = """import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
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
              <Navbar />
              
              <main>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<Placeholder title="Home Page" />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
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

files = {
    os.path.join(base_dir, "pages", "LoginPage.jsx"): login_page_code,
    os.path.join(base_dir, "pages", "RegisterPage.jsx"): register_page_code,
    os.path.join(base_dir, "components", "Navbar.jsx"): navbar_code,
    os.path.join(base_dir, "App.jsx"): app_update_code,
}

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Auth UI components generated and injected into App.jsx successfully.")
