import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const CartPage = () => {
    const { items, itemCount, total, updateItem, removeItem, loading } = useCart();
    const navigate = useNavigate();
    const [updatingId, setUpdatingId] = useState(null);

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-4 py-12 animate-pulse">
                <div className="h-10 bg-slate-200 rounded w-1/4 mb-8"></div>
                <div className="flex flex-col lg:flex-row gap-8">
                    <div className="w-full lg:w-2/3 space-y-4">
                        {[1, 2].map(i => (
                            <div key={i} className="h-32 bg-slate-200 rounded-2xl"></div>
                        ))}
                    </div>
                    <div className="w-full lg:w-1/3 h-64 bg-slate-200 rounded-2xl"></div>
                </div>
            </div>
        );
    }

    if (!items || items.length === 0) {
        return (
            <div className="max-w-3xl mx-auto px-4 py-24 text-center">
                <div className="w-24 h-24 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-6">
                    <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                </div>
                <h2 className="text-3xl font-extrabold text-text mb-4">Votre panier est vide</h2>
                <p className="text-muted mb-8 text-lg">On dirait que vous n'avez pas encore ajouté de produits. Découvrez notre catalogue !</p>
                <Link to="/" className="inline-block bg-primary hover:bg-primary-dark text-white font-bold px-8 py-4 rounded-xl transition-colors shadow-lg shadow-primary/30">
                    Commencer mes achats
                </Link>
            </div>
        );
    }

    const handleUpdateQuantity = async (itemId, newQuantity) => {
        if (newQuantity < 1) return;
        setUpdatingId(itemId);
        try {
            await updateItem(itemId, newQuantity);
        } catch (error) {
            console.error("Failed to update item", error);
        } finally {
            setUpdatingId(null);
        }
    };

    const handleRemoveItem = async (itemId) => {
        setUpdatingId(itemId);
        try {
            await removeItem(itemId);
        } catch (error) {
            console.error("Failed to remove item", error);
            setUpdatingId(null);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 md:py-12">
            <h1 className="text-3xl font-extrabold text-text mb-8">Mon Panier ({itemCount} articles)</h1>

            <div className="flex flex-col lg:flex-row gap-8 items-start">
                {/* Cart Items */}
                <div className="w-full lg:w-2/3 space-y-4">
                    {items.map((item) => {
                        const product = item.product_details;
                        if (!product) return null;

                        const hasDiscount = parseFloat(product.discount_price) > 0 && parseFloat(product.discount_price) < parseFloat(product.price);
                        const displayPrice = hasDiscount ? product.discount_price : product.price;
                        
                        let finalPrice = parseFloat(displayPrice);
                        if (item.variant && product.variants) {
                            const variantObj = product.variants.find(v => v.id === item.variant);
                            if (variantObj) finalPrice += parseFloat(variantObj.additional_price || 0);
                        }

                        const imageUrl = product.main_image || 'https://placehold.co/400x400/E5E7EB/A3A3A3?text=Pas+d%27image';

                        return (
                            <div key={item.id} className={`bg-white border border-border rounded-2xl p-4 flex gap-4 md:gap-6 relative transition-opacity ${updatingId === item.id ? 'opacity-50 pointer-events-none' : ''}`}>
                                <Link to={`/products/${product.id}`} className="w-24 h-24 md:w-32 md:h-32 flex-shrink-0 bg-bg rounded-xl overflow-hidden block">
                                    <img src={imageUrl} alt={product.name} className="w-full h-full object-cover" />
                                </Link>
                                
                                <div className="flex-1 flex flex-col">
                                    <div className="flex justify-between items-start gap-4">
                                        <div>
                                            <span className="text-xs font-semibold text-primary mb-1 block">{product.shop_name}</span>
                                            <Link to={`/products/${product.id}`} className="text-lg md:text-xl font-bold text-text hover:text-primary transition-colors line-clamp-2 leading-tight mb-2">
                                                {product.name}
                                            </Link>
                                        </div>
                                        <button 
                                            onClick={() => handleRemoveItem(item.id)}
                                            className="text-muted hover:text-error transition-colors p-1"
                                            title="Retirer l'article"
                                        >
                                            <svg className="w-5 h-5 md:w-6 md:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                        </button>
                                    </div>

                                    <div className="mt-auto flex flex-col md:flex-row items-start md:items-end justify-between gap-4">
                                        <div className="flex items-center border-2 border-border rounded-xl">
                                            <button 
                                                onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}
                                                className="w-10 h-10 flex items-center justify-center text-text hover:text-primary transition-colors text-xl font-bold"
                                            >-</button>
                                            <span className="w-10 text-center font-bold text-text">{item.quantity}</span>
                                            <button 
                                                onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                                                className="w-10 h-10 flex items-center justify-center text-text hover:text-primary transition-colors text-xl font-bold"
                                            >+</button>
                                        </div>

                                        <div className="text-right">
                                            <div className="text-xs text-muted font-medium mb-1">{parseInt(finalPrice).toLocaleString('fr-FR')} BIF / unité</div>
                                            <div className="text-xl font-black text-primary">
                                                {(finalPrice * item.quantity).toLocaleString('fr-FR')} BIF
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Order Summary */}
                <div className="w-full lg:w-1/3 bg-white border border-border rounded-2xl p-6 sticky top-24 shadow-sm">
                    <h2 className="text-xl font-bold text-text mb-6 pb-4 border-b border-border/50">Résumé de la commande</h2>
                    
                    <div className="space-y-4 mb-6">
                        <div className="flex justify-between items-center text-muted">
                            <span>Sous-total ({itemCount} articles)</span>
                            <span className="font-semibold text-text">{total.toLocaleString('fr-FR')} BIF</span>
                        </div>
                        <div className="flex justify-between items-center text-muted">
                            <span>Frais de livraison</span>
                            <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-md font-medium">Calculés à l'étape suivante</span>
                        </div>
                    </div>

                    <div className="flex justify-between items-center py-4 border-t border-b border-border/50 mb-6">
                        <span className="font-bold text-text text-lg">Total</span>
                        <span className="text-2xl font-black text-primary">{total.toLocaleString('fr-FR')} BIF</span>
                    </div>

                    <button 
                        onClick={() => navigate('/checkout')}
                        className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/30 transition-all flex items-center justify-center gap-2"
                    >
                        Passer à la caisse
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    </button>
                    
                    <div className="mt-4 flex items-center justify-center gap-2 text-muted text-sm">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                        Paiement 100% sécurisé
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CartPage;
