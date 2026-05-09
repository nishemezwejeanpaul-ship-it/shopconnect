import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

const SellerProductFormPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const isEdit = !!id;

    const [formData, setFormData] = useState({
        name: '',
        category: '',
        description: '',
        price: '',
        discount_price: '',
        stock_quantity: '',
        condition: 'new',
        status: 'active'
    });

    const [error, setError] = useState('');

    const { data: categories } = useQuery({
        queryKey: ['categories'],
        queryFn: async () => {
            const { data } = await api.get('/catalog/categories/');
            return data.data;
        }
    });

    const { data: product } = useQuery({
        queryKey: ['seller-product', id],
        queryFn: async () => {
            const { data } = await api.get(`/catalog/seller/products/${id}/`);
            return data.data;
        },
        enabled: isEdit
    });

    useEffect(() => {
        if (product) {
            setFormData({
                name: product.name,
                category: product.category,
                description: product.description,
                price: product.price,
                discount_price: product.discount_price || '',
                stock_quantity: product.stock_quantity,
                condition: product.condition,
                status: product.status
            });
        }
    }, [product]);

    const mutation = useMutation({
        mutationFn: (data) => {
            if (isEdit) {
                return api.put(`/catalog/seller/products/${id}/`, data);
            }
            return api.post('/catalog/seller/products/', data);
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['seller-products']);
            navigate('/seller/products');
        },
        onError: (err) => {
            setError(err.response?.data?.error?.message || "Une erreur est survenue.");
        }
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        mutation.mutate(formData);
    };

    const inputClasses = "w-full p-4 rounded-2xl bg-slate-50 border-2 border-slate-50 focus:border-emerald-500 focus:bg-white transition-all outline-none text-slate-900 font-medium placeholder:text-slate-300";
    const labelClasses = "block text-xs font-black text-slate-400 uppercase tracking-widest mb-2 pl-1";

    return (
        <div className="max-w-5xl mx-auto py-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-4">
                    <button onClick={() => navigate(-1)} className="w-12 h-12 bg-white border border-slate-200 rounded-2xl flex items-center justify-center hover:bg-slate-50 transition-colors shadow-sm">
                        <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" /></svg>
                    </button>
                    <div>
                        <h1 className="text-2xl font-black text-slate-900">{isEdit ? 'Modifier le Produit' : 'Ajouter un Nouveau Produit'}</h1>
                        <p className="text-sm text-slate-500 font-medium">{isEdit ? 'Mettez à jour les détails de votre article' : 'Remplissez les informations pour mettre votre article en vente'}</p>
                    </div>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Left Column: General Info */}
                    <div className="lg:col-span-2 space-y-8">
                        <section className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-6">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="w-8 h-8 bg-emerald-50 text-emerald-600 rounded-lg flex items-center justify-center">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                </div>
                                <h2 className="text-lg font-black text-slate-800">Informations Générales</h2>
                            </div>
                            
                            <div className="space-y-6">
                                <div>
                                    <label className={labelClasses}>Nom du Produit</label>
                                    <input 
                                        required
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => setFormData({...formData, name: e.target.value})}
                                        className={inputClasses}
                                        placeholder="ex: iPhone 15 Pro Max"
                                    />
                                </div>
                                
                                <div>
                                    <label className={labelClasses}>Description Détaillée</label>
                                    <textarea 
                                        rows="6"
                                        value={formData.description}
                                        onChange={(e) => setFormData({...formData, description: e.target.value})}
                                        className={inputClasses}
                                        placeholder="Décrivez les caractéristiques, l'état et les avantages de votre produit..."
                                    ></textarea>
                                </div>
                            </div>
                        </section>

                        <section className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-6">
                            <div className="flex items-center gap-3 mb-2">
                                <div className="w-8 h-8 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                </div>
                                <h2 className="text-lg font-black text-slate-800">Prix & Stock</h2>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div>
                                    <label className={labelClasses}>Prix Standard (BIF)</label>
                                    <input 
                                        required
                                        type="number"
                                        value={formData.price}
                                        onChange={(e) => setFormData({...formData, price: e.target.value})}
                                        className={inputClasses}
                                    />
                                </div>
                                <div>
                                    <label className={labelClasses}>Prix Promo (Optionnel)</label>
                                    <input 
                                        type="number"
                                        value={formData.discount_price}
                                        onChange={(e) => setFormData({...formData, discount_price: e.target.value})}
                                        className={inputClasses}
                                    />
                                </div>
                                <div>
                                    <label className={labelClasses}>Quantité en Stock</label>
                                    <input 
                                        required
                                        type="number"
                                        value={formData.stock_quantity}
                                        onChange={(e) => setFormData({...formData, stock_quantity: e.target.value})}
                                        className={inputClasses}
                                    />
                                </div>
                            </div>
                        </section>
                    </div>

                    {/* Right Column: Categorization & Status */}
                    <div className="space-y-8">
                        <section className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm space-y-6">
                            <h2 className="text-lg font-black text-slate-800 mb-2">Classification</h2>
                            
                            <div className="space-y-6">
                                <div>
                                    <label className={labelClasses}>Catégorie</label>
                                    <select 
                                        required
                                        value={formData.category}
                                        onChange={(e) => setFormData({...formData, category: e.target.value})}
                                        className={inputClasses}
                                    >
                                        <option value="">-- Choisir --</option>
                                        {categories?.map(cat => (
                                            <option key={cat.id} value={cat.id}>{cat.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className={labelClasses}>État de l'article</label>
                                    <select 
                                        value={formData.condition}
                                        onChange={(e) => setFormData({...formData, condition: e.target.value})}
                                        className={inputClasses}
                                    >
                                        <option value="new">Neuf</option>
                                        <option value="used">Occasion</option>
                                        <option value="refurbished">Remis à neuf</option>
                                    </select>
                                </div>
                                <div>
                                    <label className={labelClasses}>Visibilité</label>
                                    <select 
                                        value={formData.status}
                                        onChange={(e) => setFormData({...formData, status: e.target.value})}
                                        className={inputClasses}
                                    >
                                        <option value="active">🟢 Actif (En ligne)</option>
                                        <option value="draft">🟡 Brouillon (Caché)</option>
                                        <option value="paused">🟠 En pause</option>
                                    </select>
                                </div>
                            </div>
                        </section>

                        <div className="bg-emerald-900 p-8 rounded-[2.5rem] text-white shadow-xl shadow-emerald-900/20">
                            <h3 className="font-black mb-2 italic">Astuce Pro</h3>
                            <p className="text-sm opacity-80 leading-relaxed font-medium">Une description claire et précise augmente vos chances de vente de 40%. N'oubliez pas de mentionner les garanties éventuelles.</p>
                        </div>
                    </div>
                </div>

                {error && <div className="p-4 bg-red-50 text-red-600 rounded-2xl text-sm font-bold border border-red-100">{error}</div>}

                <div className="flex justify-end items-center gap-6 pt-4">
                    <button type="button" onClick={() => navigate(-1)} className="text-slate-400 font-black hover:text-slate-600 transition-colors uppercase tracking-widest text-xs">Annuler</button>
                    <button 
                        disabled={mutation.isPending}
                        type="submit" 
                        className="px-12 py-5 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-600/30 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50"
                    >
                        {mutation.isPending ? 'Enregistrement...' : isEdit ? 'Mettre à jour le Produit' : 'Mettre en Vente'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default SellerProductFormPage;
