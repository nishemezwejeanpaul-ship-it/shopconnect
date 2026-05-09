import os

src_dir = r"E:\project\shopconnect\frontend\src"

# 1. ProductCard.jsx
product_card_code = """import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const ProductCard = ({ product }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mainImage = product.images?.find((img) => img.is_main) || product.images?.[0];
  const imageUrl = mainImage?.image_url || 'https://placehold.co/400x400/E5E7EB/A3A3A3?text=Pas+d%27image';
  
  const hasDiscount = parseFloat(product.discount_price) > 0 && parseFloat(product.discount_price) < parseFloat(product.price);
  const displayPrice = hasDiscount ? product.discount_price : product.price;

  // Global Wishlist Query
  const { data: wishlistData } = useQuery({
    queryKey: ['wishlist'],
    queryFn: async () => {
        const { data } = await api.get('/catalog/wishlist/');
        // Handle both paginated and flat responses safely
        return data.data?.results || data.data || [];
    },
    enabled: !!user,
  });

  const wishlistItems = wishlistData || [];
  const isInWishlist = wishlistItems.some(item => item.product === product.id);

  // Optimistic Mutation
  const toggleWishlist = useMutation({
    mutationFn: async (isAdding) => {
        if (isAdding) {
            await api.post('/catalog/wishlist/add/', { product_id: product.id });
        } else {
            await api.delete(`/catalog/wishlist/remove/${product.id}/`);
        }
    },
    onMutate: async (isAdding) => {
        await queryClient.cancelQueries({ queryKey: ['wishlist'] });
        const previousWishlist = queryClient.getQueryData(['wishlist']);
        
        queryClient.setQueryData(['wishlist'], (old) => {
            const oldList = old?.results || old || [];
            if (isAdding) {
                // Add fake item
                return [{ id: 'temp', product: product.id, product_details: product }, ...oldList];
            } else {
                // Remove item
                return oldList.filter(item => item.product !== product.id);
            }
        });
        
        return { previousWishlist };
    },
    onError: (err, newTodo, context) => {
        queryClient.setQueryData(['wishlist'], context.previousWishlist);
    },
    onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ['wishlist'] });
    },
  });

  const handleWishlistClick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!user) {
          navigate('/login');
          return;
      }
      toggleWishlist.mutate(!isInWishlist);
  };

  return (
    <div className="bg-white rounded-2xl border border-border overflow-hidden flex flex-col hover:shadow-xl transition-shadow duration-300 relative">
      <div className="aspect-square bg-bg relative group">
        <img src={imageUrl} alt={product.name} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
        
        {/* Wishlist Button */}
        <button 
            onClick={handleWishlistClick}
            className="absolute top-2 right-2 p-2 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white transition-colors shadow-sm z-10"
        >
            <svg 
                className={`w-5 h-5 transition-colors ${isInWishlist ? 'text-red-500 fill-red-500' : 'text-slate-400 fill-transparent hover:text-red-500'}`} 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                strokeWidth="2"
            >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
        </button>

        {hasDiscount && (
          <span className="absolute top-2 left-2 bg-error text-white text-xs font-bold px-2 py-1 rounded-full shadow-sm z-10">
            Promo
          </span>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <span className="text-xs text-muted mb-1 font-medium">{product.shop?.name || product.shop_name || 'Boutique inconnue'}</span>
        <h3 className="text-text font-bold text-sm md:text-base line-clamp-2 mb-2 flex-1">{product.name}</h3>
        <div className="mb-4">
          <span className="text-primary font-extrabold text-lg">{parseInt(displayPrice).toLocaleString('fr-FR')} BIF</span>
          {hasDiscount && (
            <span className="text-muted line-through text-xs ml-2 block sm:inline">{parseInt(product.price).toLocaleString('fr-FR')} BIF</span>
          )}
        </div>
        <Link 
          to={`/products/${product.id}`}
          className="w-full text-center bg-primary/10 text-primary hover:bg-primary hover:text-white font-semibold py-2 rounded-xl transition-colors mt-auto"
        >
          Voir le produit
        </Link>
      </div>
    </div>
  );
};

export default ProductCard;
"""

# 2. HomePage.jsx
home_page_code = """import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import api from '../services/api';
import ProductCard from '../components/ProductCard';
import SkeletonCard from '../components/SkeletonCard';

const fetchCategories = async () => {
    const { data } = await api.get('/catalog/categories/');
    return data.data || [];
};

const fetchProducts = async ({ pageParam = 1, queryKey }) => {
    const [_key, params] = queryKey;
    const { data } = await api.get('/catalog/products/', { 
        params: { ...params, page: pageParam }
    });
    return data.data;
};

const HomePage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const currentSearch = searchParams.get('search') || '';
    const currentCategory = searchParams.get('category') || '';
    const currentMinPrice = searchParams.get('min_price') || '';
    const currentMaxPrice = searchParams.get('max_price') || '';

    const [searchInput, setSearchInput] = useState(currentSearch);
    const [minPriceInput, setMinPriceInput] = useState(currentMinPrice);
    const [maxPriceInput, setMaxPriceInput] = useState(currentMaxPrice);

    useEffect(() => {
        setSearchInput(currentSearch);
        setMinPriceInput(currentMinPrice);
        setMaxPriceInput(currentMaxPrice);
    }, [currentSearch, currentMinPrice, currentMaxPrice]);

    const { data: categories = [], isLoading: catsLoading } = useQuery({
        queryKey: ['categories'],
        queryFn: fetchCategories,
    });

    const { 
        data: productsData, 
        isLoading: prodsLoading,
        isFetchingNextPage,
        hasNextPage,
        fetchNextPage
    } = useInfiniteQuery({
        queryKey: ['products', { search: currentSearch, category: currentCategory, min_price: currentMinPrice, max_price: currentMaxPrice }],
        queryFn: fetchProducts,
        initialPageParam: 1,
        getNextPageParam: (lastPage, allPages) => {
            if (lastPage && lastPage.next) {
                return allPages.length + 1;
            }
            return undefined;
        }
    });

    const productList = productsData ? productsData.pages.flatMap(p => Array.isArray(p) ? p : (p?.results || [])) : [];

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        const newParams = new URLSearchParams(searchParams);
        if (searchInput) newParams.set('search', searchInput);
        else newParams.delete('search');
        setSearchParams(newParams);
    };

    const handleCategoryClick = (categoryId) => {
        const newParams = new URLSearchParams(searchParams);
        if (categoryId === 'all') {
            newParams.delete('category');
        } else {
            newParams.set('category', categoryId);
        }
        setSearchParams(newParams);
    };

    const handlePriceFilter = (e) => {
        e.preventDefault();
        const newParams = new URLSearchParams(searchParams);
        if (minPriceInput) newParams.set('min_price', minPriceInput);
        else newParams.delete('min_price');
        
        if (maxPriceInput) newParams.set('max_price', maxPriceInput);
        else newParams.delete('max_price');
        
        setSearchParams(newParams);
    };

    const colors = ['bg-blue-500', 'bg-amber-500', 'bg-emerald-500', 'bg-purple-500', 'bg-rose-500', 'bg-indigo-500'];

    return (
        <div className="pb-16">
            {/* Hero Section */}
            <section className="bg-primary pt-16 pb-24 px-4 text-center text-white relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-primary-dark to-primary opacity-80 z-0"></div>
                <div className="relative z-10 max-w-3xl mx-auto">
                    <h1 className="text-4xl md:text-5xl font-extrabold mb-6 tracking-tight">
                        Achetez dans les meilleurs dukas du Burundi
                    </h1>
                    <form onSubmit={handleSearchSubmit} className="relative max-w-2xl mx-auto">
                        <input 
                            type="text" 
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="Rechercher un produit, une marque..." 
                            className="w-full px-6 py-4 rounded-full text-text bg-white shadow-xl focus:outline-none focus:ring-4 focus:ring-accent/50"
                        />
                        <button type="submit" className="absolute right-2 top-2 bottom-2 bg-accent hover:bg-amber-600 text-white px-6 font-bold rounded-full transition-colors shadow-sm">
                            Rechercher
                        </button>
                    </form>
                </div>
            </section>

            {/* Categories Section - Grid Upgrade */}
            <section className="max-w-7xl mx-auto px-4 -mt-10 relative z-20 mb-12">
                <div className="bg-white rounded-2xl shadow-lg border border-border p-6">
                    <h2 className="text-lg font-bold text-text mb-4">Catégories</h2>
                    <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                        
                        {/* Static 'All Categories' Card */}
                        <button 
                            onClick={() => handleCategoryClick('all')}
                            className={`group relative aspect-square rounded-xl overflow-hidden shadow-sm transition-all ${
                                !currentCategory ? 'ring-4 ring-primary ring-offset-2 scale-105 z-10' : 'hover:shadow-md'
                            }`}
                        >
                            <div className="absolute inset-0 bg-gradient-to-br from-slate-700 to-slate-900 transition-transform duration-300 group-hover:scale-110"></div>
                            <div className="absolute inset-0 flex items-center justify-center p-2">
                                <span className="text-white font-bold text-sm text-center drop-shadow-md">Toutes les catégories</span>
                            </div>
                        </button>

                        {catsLoading ? (
                            [...Array(5)].map((_, i) => <div key={i} className="aspect-square bg-slate-100 animate-pulse rounded-xl" />)
                        ) : categories.length === 0 ? (
                            /* Fallback Empty Category State */
                            <div className="col-span-2 md:col-span-5 text-muted text-sm flex items-center p-4 bg-bg rounded-xl border border-border">
                                Aucune catégorie disponible.
                            </div>
                        ) : (
                            categories.map((cat, i) => {
                                const isSelected = currentCategory === String(cat.id);
                                const fallbackColor = colors[i % colors.length];
                                
                                return (
                                    <button 
                                        key={cat.id} 
                                        onClick={() => handleCategoryClick(cat.id)}
                                        className={`group relative aspect-square rounded-xl overflow-hidden shadow-sm transition-all ${
                                            isSelected ? 'ring-4 ring-primary ring-offset-2 scale-105 z-10' : 'hover:shadow-md'
                                        }`}
                                    >
                                        {cat.photo_url ? (
                                            <img 
                                                src={cat.photo_url} 
                                                alt={cat.name} 
                                                className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" 
                                            />
                                        ) : (
                                            <div className={`absolute inset-0 ${fallbackColor} transition-transform duration-500 group-hover:scale-110`}></div>
                                        )}
                                        {/* Dark Gradient Overlay */}
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                                        
                                        {/* Text Overlaid */}
                                        <div className="absolute bottom-0 left-0 right-0 p-3 text-center">
                                            <span className="text-white font-bold text-xs sm:text-sm drop-shadow-md line-clamp-2">
                                                {cat.name}
                                            </span>
                                        </div>
                                    </button>
                                );
                            })
                        )}
                    </div>
                </div>
            </section>

            {/* Main Content */}
            <section className="max-w-7xl mx-auto px-4 mt-8 flex flex-col md:flex-row gap-8">
                {/* Filters Sidebar */}
                <aside className="w-full md:w-64 flex-shrink-0">
                    <div className="bg-white p-6 rounded-2xl border border-border shadow-sm sticky top-24">
                        <h3 className="font-bold text-lg mb-4 text-text">Filtres</h3>
                        
                        <form onSubmit={handlePriceFilter}>
                            <h4 className="font-semibold text-sm mb-3 text-text">Prix (BIF)</h4>
                            <div className="flex items-center gap-2 mb-4">
                                <input 
                                    type="number" 
                                    placeholder="Min" 
                                    value={minPriceInput}
                                    onChange={(e) => setMinPriceInput(e.target.value)}
                                    className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-bg focus:ring-2 focus:ring-primary outline-none"
                                />
                                <span className="text-muted">-</span>
                                <input 
                                    type="number" 
                                    placeholder="Max" 
                                    value={maxPriceInput}
                                    onChange={(e) => setMaxPriceInput(e.target.value)}
                                    className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-bg focus:ring-2 focus:ring-primary outline-none"
                                />
                            </div>
                            <button type="submit" className="w-full bg-primary/10 text-primary font-bold py-2 rounded-lg hover:bg-primary hover:text-white transition-colors text-sm">
                                Appliquer
                            </button>
                        </form>
                    </div>
                </aside>

                {/* Products Grid */}
                <div className="flex-1">
                    <div className="mb-6 flex justify-between items-center">
                        <h2 className="text-2xl font-bold text-text">
                            {currentSearch ? `Résultats pour "${currentSearch}"` : 'Tous les produits'}
                        </h2>
                    </div>

                    {prodsLoading ? (
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                            {[...Array(8)].map((_, i) => <SkeletonCard key={i} />)}
                        </div>
                    ) : productList.length === 0 ? (
                        <div className="bg-white p-12 rounded-2xl border border-border text-center">
                            <svg className="w-16 h-16 text-muted mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                            </svg>
                            <h3 className="text-xl font-bold text-text mb-2">Aucun produit trouvé</h3>
                            <p className="text-muted">Essayez de modifier vos filtres ou votre recherche.</p>
                        </div>
                    ) : (
                        <>
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
                                {productList.map(product => (
                                    <ProductCard key={product.id} product={product} />
                                ))}
                            </div>
                            
                            {hasNextPage && (
                                <div className="mt-10 text-center">
                                    <button 
                                        onClick={() => fetchNextPage()}
                                        disabled={isFetchingNextPage}
                                        className="bg-white border-2 border-primary text-primary hover:bg-primary hover:text-white font-bold py-3 px-8 rounded-full transition-colors disabled:opacity-50 shadow-sm hover:shadow-md"
                                    >
                                        {isFetchingNextPage ? 'Chargement...' : 'Voir plus'}
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </section>
        </div>
    );
};

export default HomePage;
"""

with open(os.path.join(src_dir, "components", "ProductCard.jsx"), "w", encoding="utf-8") as f:
    f.write(product_card_code)

with open(os.path.join(src_dir, "pages", "HomePage.jsx"), "w", encoding="utf-8") as f:
    f.write(home_page_code)

print("Frontend components upgraded successfully.")
