import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { TableSkeleton } from '../components/SellerSkeleton';

const SellerProductsPage = () => {
    const queryClient = useQueryClient();
    const { data: products, isLoading } = useQuery({
        queryKey: ['seller-products'],
        queryFn: async () => {
            const { data } = await api.get('/catalog/seller/products/');
            return data.data;
        }
    });

    const deleteMutation = useMutation({
        mutationFn: (id) => api.delete(`/catalog/seller/products/${id}/`),
        onSuccess: () => {
            queryClient.invalidateQueries(['seller-products']);
        }
    });

    const handleDelete = (id) => {
        if (window.confirm('Voulez-vous vraiment retirer ce produit de la vente ?')) {
            deleteMutation.mutate(id);
        }
    };

    if (isLoading) return <TableSkeleton />;

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 mb-1">Catalogue Produits</h1>
                    <p className="text-slate-500 font-medium">Gérez votre inventaire, vos prix et la visibilité de vos articles.</p>
                </div>
                <Link to="/seller/products/new" className="px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-600/30 hover:scale-[1.05] active:scale-95 transition-all flex items-center gap-3">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M12 4v16m8-8H4" /></svg>
                    Nouveau Produit
                </Link>
            </div>

            <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-50/50">
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Produit</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Catégorie</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Stock</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Prix</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Status</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {products?.map((product, idx) => (
                                <tr key={product.id} className={`${idx % 2 === 1 ? 'bg-slate-50/20' : 'bg-white'} hover:bg-emerald-50/30 transition-colors group`}>
                                    <td className="px-8 py-6">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-xl border border-slate-100 overflow-hidden bg-slate-50 shadow-sm">
                                                <img src={product.main_image || 'https://placehold.co/100x100'} alt="" className="w-full h-full object-cover" />
                                            </div>
                                            <span className="font-black text-slate-900 text-sm line-clamp-1">{product.name}</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className="text-xs font-black text-slate-400 uppercase tracking-widest">{product.category_name}</span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className={`font-bold text-sm ${product.stock_quantity <= 5 ? 'text-red-500' : 'text-slate-600'}`}>
                                            {product.stock_quantity} <span className="text-[10px] opacity-50 uppercase ml-1">unités</span>
                                        </span>
                                    </td>
                                    <td className="px-8 py-6 font-black text-slate-900 text-sm">
                                        {parseFloat(product.price).toLocaleString()} <span className="text-[10px] text-slate-400">BIF</span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest inline-flex items-center gap-2 ${
                                            product.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'
                                        }`}>
                                            <span className={`w-1 h-1 rounded-full ${product.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
                                            {product.status}
                                        </span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="flex justify-end items-center gap-3">
                                            <Link 
                                                to={`/seller/products/${product.id}/edit`}
                                                className="w-10 h-10 bg-white border border-slate-100 rounded-xl flex items-center justify-center text-slate-400 hover:text-emerald-600 hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-100 transition-all"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>
                                            </Link>
                                            <button 
                                                onClick={() => handleDelete(product.id)}
                                                className="w-10 h-10 bg-white border border-slate-100 rounded-xl flex items-center justify-center text-slate-400 hover:text-red-500 hover:border-red-200 hover:shadow-lg hover:shadow-red-100 transition-all"
                                            >
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default SellerProductsPage;
