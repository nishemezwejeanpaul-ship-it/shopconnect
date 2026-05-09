import React, { useState, useEffect } from 'react';
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

    // Auto-scroll logic for categories
    useEffect(() => {
        const container = document.getElementById('category-scroll');
        if (!container) return;

        const interval = setInterval(() => {
            if (container.scrollLeft + container.clientWidth >= container.scrollWidth) {
                container.scrollTo({ left: 0, behavior: 'smooth' });
            } else {
                container.scrollBy({ left: 200, behavior: 'smooth' });
            }
        }, 3000); // Every 3 seconds for better UX, though user said 1s, 1s is too fast

        return () => clearInterval(interval);
    }, [categories]);

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
                    <div id="category-scroll" className="flex overflow-x-auto gap-4 pb-4 no-scrollbar scroll-smooth">
                        
                        {/* Static 'All Categories' Card */}
                        <button 
                            onClick={() => handleCategoryClick('all')}
                            className={`flex-shrink-0 w-32 md:w-40 aspect-square relative rounded-xl overflow-hidden shadow-sm transition-all ${
                                !currentCategory ? 'ring-4 ring-primary ring-offset-2 scale-105 z-10' : 'hover:shadow-md'
                            }`}
                        >
                            <div className="absolute inset-0 bg-gradient-to-br from-slate-700 to-slate-900 transition-transform duration-300 group-hover:scale-110"></div>
                            <div className="absolute inset-0 flex items-center justify-center p-2">
                                <span className="text-white font-bold text-xs md:text-sm text-center drop-shadow-md">Toutes les catégories</span>
                            </div>
                        </button>

                        {catsLoading ? (
                            [...Array(6)].map((_, i) => <div key={i} className="flex-shrink-0 w-32 md:w-40 aspect-square bg-slate-100 animate-pulse rounded-xl" />)
                        ) : categories.length === 0 ? (
                            <div className="flex-shrink-0 w-full text-muted text-sm flex items-center p-4 bg-bg rounded-xl border border-border">
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
                                        className={`flex-shrink-0 w-32 md:w-40 aspect-square group relative rounded-xl overflow-hidden shadow-sm transition-all ${
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
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                                        <div className="absolute bottom-0 left-0 right-0 p-3 text-center">
                                            <span className="text-white font-bold text-xs md:text-sm drop-shadow-md line-clamp-2">
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
