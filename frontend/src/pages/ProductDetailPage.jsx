import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';

const fetchProduct = async (id) => {
    const { data } = await api.get(`/catalog/products/${id}/`);
    return data.data;
};

const ProductDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { addItem } = useCart();
    const { user } = useAuth();
    
    const [quantity, setQuantity] = useState(1);
    const [selectedImage, setSelectedImage] = useState(0);
    const [addingToCart, setAddingToCart] = useState(false);
    
    const { data: product, isLoading, isError } = useQuery({
        queryKey: ['product', id],
        queryFn: () => fetchProduct(id),
    });

    if (isLoading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-12 animate-pulse">
                <div className="flex flex-col md:flex-row gap-10">
                    <div className="w-full md:w-1/2 bg-slate-200 aspect-square rounded-2xl"></div>
                    <div className="w-full md:w-1/2 space-y-6">
                        <div className="h-10 bg-slate-200 rounded w-3/4"></div>
                        <div className="h-6 bg-slate-200 rounded w-1/4"></div>
                        <div className="h-12 bg-slate-200 rounded w-1/3"></div>
                        <div className="h-40 bg-slate-200 rounded w-full"></div>
                        <div className="h-14 bg-slate-200 rounded w-full"></div>
                    </div>
                </div>
            </div>
        );
    }

    if (isError || !product) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-20 text-center">
                <h2 className="text-2xl font-bold text-text mb-4">Produit introuvable</h2>
                <button onClick={() => navigate('/')} className="text-primary hover:underline">
                    Retour à l'accueil
                </button>
            </div>
        );
    }

    const hasDiscount = parseFloat(product.discount_price) > 0 && parseFloat(product.discount_price) < parseFloat(product.price);
    const displayPrice = hasDiscount ? product.discount_price : product.price;

    const allImages = product.images?.length > 0 
        ? product.images 
        : [{ image_url: 'https://placehold.co/800x800/E5E7EB/A3A3A3?text=Pas+d%27image' }];

    const handleAddToCart = async () => {
        if (!user) {
            navigate('/login');
            return;
        }
        setAddingToCart(true);
        try {
            await addItem(product.id, quantity);
            // Optionally show a success toast here
        } catch (error) {
            console.error("Failed to add to cart", error);
        } finally {
            setAddingToCart(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 md:py-12">
            <div className="flex flex-col md:flex-row gap-10 lg:gap-16">
                
                {/* Image Gallery */}
                <div className="w-full md:w-1/2 flex flex-col gap-4">
                    <div className="bg-bg aspect-square rounded-3xl overflow-hidden border border-border relative">
                        <img 
                            src={allImages[selectedImage]?.image_url} 
                            alt={product.name}
                            className="w-full h-full object-cover"
                        />
                        {hasDiscount && (
                            <span className="absolute top-4 left-4 bg-error text-white text-sm font-bold px-3 py-1 rounded-full shadow-md">
                                Promo
                            </span>
                        )}
                    </div>
                    {allImages.length > 1 && (
                        <div className="flex gap-4 overflow-x-auto pb-2">
                            {allImages.map((img, idx) => (
                                <button 
                                    key={idx}
                                    onClick={() => setSelectedImage(idx)}
                                    className={`w-20 h-20 flex-shrink-0 rounded-xl overflow-hidden border-2 transition-all ${
                                        selectedImage === idx ? 'border-primary shadow-md' : 'border-transparent opacity-70 hover:opacity-100'
                                    }`}
                                >
                                    <img src={img.image_url} alt="Thumbnail" className="w-full h-full object-cover" />
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Product Info */}
                <div className="w-full md:w-1/2 flex flex-col">
                    <div className="mb-2 flex items-center justify-between">
                        <span className="text-sm font-semibold text-primary bg-primary/10 px-3 py-1 rounded-full">
                            {product.category_name}
                        </span>
                        <span className="text-sm text-muted">
                            Vendu par <span className="font-bold text-text">{product.shop_name}</span>
                        </span>
                    </div>
                    
                    <h1 className="text-3xl md:text-4xl font-extrabold text-text mb-4 leading-tight">
                        {product.name}
                    </h1>

                    <div className="mb-6 flex items-baseline gap-4">
                        <span className="text-4xl font-black text-primary">
                            {parseInt(displayPrice).toLocaleString('fr-FR')} BIF
                        </span>
                        {hasDiscount && (
                            <span className="text-xl text-muted line-through font-medium">
                                {parseInt(product.price).toLocaleString('fr-FR')} BIF
                            </span>
                        )}
                    </div>

                    <div className="bg-bg rounded-2xl p-6 mb-8 border border-border">
                        <div className="flex items-center justify-between mb-4 pb-4 border-b border-border/50">
                            <span className="text-muted font-medium">État</span>
                            <span className="font-bold text-text capitalize">
                                {product.condition === 'new' ? 'Neuf' : product.condition === 'used' ? 'Occasion' : 'Reconditionné'}
                            </span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-muted font-medium">Disponibilité</span>
                            {product.stock_quantity > 0 ? (
                                <span className="font-bold text-emerald-600 bg-emerald-100 px-3 py-1 rounded-full text-sm">
                                    En stock ({product.stock_quantity})
                                </span>
                            ) : (
                                <span className="font-bold text-error bg-error/10 px-3 py-1 rounded-full text-sm">
                                    Rupture de stock
                                </span>
                            )}
                        </div>
                    </div>

                    <div className="mb-8">
                        <h3 className="text-lg font-bold text-text mb-3">Description</h3>
                        <p className="text-muted leading-relaxed whitespace-pre-line">
                            {product.description || "Aucune description fournie pour ce produit."}
                        </p>
                    </div>

                    {/* Add to Cart Area */}
                    <div className="mt-auto pt-6 border-t border-border flex gap-4">
                        <div className="flex items-center border-2 border-border rounded-xl px-2">
                            <button 
                                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                                className="w-10 h-10 flex items-center justify-center text-text hover:text-primary transition-colors text-xl font-bold"
                            >-</button>
                            <span className="w-12 text-center font-bold text-text">{quantity}</span>
                            <button 
                                onClick={() => setQuantity(Math.min(product.stock_quantity, quantity + 1))}
                                className="w-10 h-10 flex items-center justify-center text-text hover:text-primary transition-colors text-xl font-bold"
                            >+</button>
                        </div>
                        <button 
                            onClick={handleAddToCart}
                            disabled={addingToCart || product.stock_quantity < 1}
                            className="flex-1 bg-primary hover:bg-primary-dark text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/30 transition-all disabled:opacity-50 disabled:shadow-none flex items-center justify-center gap-2"
                        >
                            {addingToCart ? (
                                <span>Ajout en cours...</span>
                            ) : (
                                <>
                                    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                    </svg>
                                    Ajouter au panier
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProductDetailPage;
