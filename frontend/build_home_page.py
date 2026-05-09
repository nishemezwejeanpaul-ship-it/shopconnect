import os

src_dir = r"E:\project\shopconnect\frontend\src"

product_card_code = """import React from 'react';
import { Link } from 'react-router-dom';

const ProductCard = ({ product }) => {
  const mainImage = product.images?.find((img) => img.is_main) || product.images?.[0];
  const imageUrl = mainImage?.image || 'https://placehold.co/400x400/E5E7EB/A3A3A3?text=Pas+d%27image';
  
  const hasDiscount = parseFloat(product.discount_price) > 0 && parseFloat(product.discount_price) < parseFloat(product.price);
  const displayPrice = hasDiscount ? product.discount_price : product.price;

  return (
    <div className="bg-white rounded-2xl border border-border overflow-hidden flex flex-col hover:shadow-xl transition-shadow duration-300">
      <div className="aspect-square bg-bg relative">
        <img src={imageUrl} alt={product.name} className="w-full h-full object-cover" />
        {hasDiscount && (
          <span className="absolute top-2 right-2 bg-error text-white text-xs font-bold px-2 py-1 rounded-full shadow-sm">
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

skeleton_card_code = """import React from 'react';

const SkeletonCard = () => {
  return (
    <div className="bg-white rounded-2xl border border-border overflow-hidden flex flex-col animate-pulse">
      <div className="aspect-square bg-slate-200" />
      <div className="p-4 flex flex-col flex-1">
        <div className="h-3 bg-slate-200 rounded w-1/3 mb-2" />
        <div className="h-4 bg-slate-200 rounded w-3/4 mb-1" />
        <div className="h-4 bg-slate-200 rounded w-1/2 mb-4" />
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4" />
        <div className="h-10 bg-slate-200 rounded-xl w-full mt-auto" />
      </div>
    </div>
  );
};

export default SkeletonCard;
"""

home_page_code = """import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInfiniteQuery, useQuery } from '@tanstack/react-query';
import api from '../services/api';
import ProductCard from '../components/ProductCard';
import SkeletonCard from '../components/SkeletonCard';

const fetchCategories = async () => {
    const { data } = await api.get('/categories/');
    return data.data || [];
};

const fetchProducts = async ({ pageParam = 1, queryKey }) => {
    const [_key, params] = queryKey;
    const { data } = await api.get('/products/', { 
        params: { ...params, page: pageParam }
    });
    return data.data; // Expected format: { count, next, previous, results }
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

    // Sync input fields if URL changes externally
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
            // DRF pagination returning a next URL string
            if (lastPage && lastPage.next) {
                return allPages.length + 1;
            }
            return undefined;
        }
    });

    // Safely extract product list whether it's paginated or a raw array
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
        if (currentCategory === String(categoryId)) {
            newParams.delete('category'); // Toggle off
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

            {/* Categories Bar */}
            <section className="max-w-7xl mx-auto px-4 -mt-10 relative z-20">
                <div className="bg-white rounded-2xl shadow-lg border border-border p-4 flex gap-4 overflow-x-auto snap-x hide-scrollbar">
                    {catsLoading ? (
                        [...Array(6)].map((_, i) => <div key={i} className="min-w-[100px] h-24 bg-slate-100 animate-pulse rounded-xl flex-shrink-0" />)
                    ) : (
                        categories.map(cat => (
                            <button 
                                key={cat.id} 
                                onClick={() => handleCategoryClick(cat.id)}
                                className={`flex-shrink-0 snap-center flex flex-col items-center justify-center min-w-[100px] p-3 rounded-xl transition-all ${currentCategory === String(cat.id) ? 'bg-primary/10 border-primary border' : 'hover:bg-bg border border-transparent'}`}
                            >
                                <div className="w-12 h-12 rounded-full overflow-hidden mb-2 bg-bg border border-border flex items-center justify-center">
                                    {cat.image ? (
                                        <img src={cat.image} alt={cat.name} className="w-full h-full object-cover" />
                                    ) : (
                                        <span className="text-primary font-bold text-lg">{cat.name.charAt(0)}</span>
                                    )}
                                </div>
                                <span className={`text-xs font-semibold ${currentCategory === String(cat.id) ? 'text-primary' : 'text-text'}`}>{cat.name}</span>
                            </button>
                        ))
                    )}
                </div>
            </section>

            {/* Main Content */}
            <section className="max-w-7xl mx-auto px-4 mt-12 flex flex-col md:flex-row gap-8">
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
                                        className="bg-white border-2 border-primary text-primary hover:bg-primary hover:text-white font-bold py-3 px-8 rounded-full transition-colors disabled:opacity-50"
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

import sys

with open(os.path.join(src_dir, "components", "ProductCard.jsx"), "w", encoding="utf-8") as f:
    f.write(product_card_code)

with open(os.path.join(src_dir, "components", "SkeletonCard.jsx"), "w", encoding="utf-8") as f:
    f.write(skeleton_card_code)

with open(os.path.join(src_dir, "pages", "HomePage.jsx"), "w", encoding="utf-8") as f:
    f.write(home_page_code)

# Add hide-scrollbar utility to index.css
with open(os.path.join(src_dir, "index.css"), "a", encoding="utf-8") as f:
    f.write("\n.hide-scrollbar::-webkit-scrollbar { display: none; }\n.hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }\n")

# Update App.jsx
app_path = os.path.join(src_dir, "App.jsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_content = f.read()

# Add import
app_content = app_content.replace(
    "import RegisterPage from './pages/RegisterPage';",
    "import RegisterPage from './pages/RegisterPage';\nimport HomePage from './pages/HomePage';"
)

# Remove the dummy HomePage component
app_content = app_content.replace("const HomePage = () => <Placeholder title=\"Home Page\" />;\n", "")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_content)

print("Home page components built successfully.")
