import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

const SellerOrdersPage = () => {
    const queryClient = useQueryClient();
    const { data: orders, isLoading } = useQuery({
        queryKey: ['seller-orders'],
        queryFn: async () => {
            const { data } = await api.get('/orders/seller/orders/');
            return data.data;
        }
    });

    const statusMutation = useMutation({
        mutationFn: ({ orderId, status }) => api.put(`/orders/seller/orders/${orderId}/status/`, { status }),
        onSuccess: () => {
            queryClient.invalidateQueries(['seller-orders']);
        }
    });

    const handleStatusChange = (orderId, newStatus) => {
        if (!newStatus) return;
        statusMutation.mutate({ orderId, status: newStatus });
    };

    if (isLoading) return <div className="p-8 text-center text-slate-400 font-bold animate-pulse">Chargement des commandes...</div>;

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="grid grid-cols-1 gap-8">
                {orders?.map(order => (
                    <div key={order.id} className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden group hover:shadow-2xl hover:shadow-slate-200/40 transition-all border-l-8 border-l-slate-50 hover:border-l-emerald-500">
                        <div className="p-8 border-b border-slate-50 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 bg-slate-50/20">
                            <div className="space-y-2">
                                <div className="flex items-center gap-4">
                                    <span className="text-sm font-black text-slate-400 uppercase tracking-widest">Commande #SC-{order.id.slice(-8).toUpperCase()}</span>
                                    <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest bg-white border border-slate-200 text-slate-500 flex items-center gap-2`}>
                                        <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                                        {order.status}
                                    </span>
                                </div>
                                <p className="text-base font-black text-slate-900">Passée le {new Date(order.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</p>
                            </div>
                            
                            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-white p-3 rounded-2xl border border-slate-100 shadow-sm">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest pl-2">Modifier Statut</span>
                                <select 
                                    onChange={(e) => handleStatusChange(order.id, e.target.value)}
                                    className="px-4 py-2 rounded-xl border-none bg-slate-50 text-xs font-black text-emerald-600 outline-none focus:ring-2 focus:ring-emerald-500/20 cursor-pointer"
                                >
                                    <option value="">-- Sélectionner --</option>
                                    <option value="pending">⏳ En attente</option>
                                    <option value="confirmed">✅ Confirmé</option>
                                    <option value="shipping">🚚 En livraison</option>
                                    <option value="completed">🏁 Livré</option>
                                    <option value="cancelled">❌ Annulé</option>
                                </select>
                            </div>
                        </div>

                        <div className="p-8 grid grid-cols-1 xl:grid-cols-3 gap-12">
                            {/* Items Column */}
                            <div className="xl:col-span-2 space-y-6">
                                <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Articles à Expédier</h3>
                                <div className="space-y-4">
                                    {order.items?.map(item => (
                                        <div key={item.id} className="p-4 rounded-2xl border border-slate-50 hover:bg-slate-50/50 transition-colors flex items-center justify-between group/item">
                                            <div className="flex items-center gap-6">
                                                <div className="w-16 h-16 bg-white rounded-xl overflow-hidden border border-slate-100 shadow-sm group-hover/item:scale-110 transition-transform">
                                                    <img src={item.product_details?.main_image || 'https://placehold.co/100x100'} alt="" className="w-full h-full object-cover" />
                                                </div>
                                                <div>
                                                    <p className="font-black text-slate-900 text-base">{item.product_details?.name}</p>
                                                    <p className="text-xs font-bold text-slate-500">Quantité: <span className="text-emerald-600">{item.quantity}</span></p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-black text-slate-900 text-lg">{(item.total_price).toLocaleString()} <span className="text-[10px] text-slate-400">BIF</span></p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Info Column */}
                            <div className="space-y-8">
                                <div className="space-y-4">
                                    <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Destinataire</h3>
                                    <div className="bg-slate-50/50 p-6 rounded-[2rem] border border-slate-50 space-y-4">
                                        <div className="flex items-start gap-4">
                                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm text-lg">📍</div>
                                            <div>
                                                <p className="text-sm font-black text-slate-900 leading-tight mb-1">{order.shipping_address_details?.address || 'Point Relais'}</p>
                                                <p className="text-xs font-bold text-slate-400">{order.shipping_address_details?.phone || 'Contact non spécifié'}</p>
                                            </div>
                                        </div>
                                        <hr className="border-slate-100" />
                                        <div className="flex items-start gap-4">
                                            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm text-lg">💳</div>
                                            <div>
                                                <p className="text-sm font-black text-slate-900 leading-tight mb-1">{order.payment_details?.method === 'cash' ? 'Paiement à la Livraison' : 'Mobile Money'}</p>
                                                <p className="text-xs font-bold text-emerald-600 uppercase tracking-widest">Part Boutique: {order.total_amount.toLocaleString()} BIF</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
                {(!orders || orders.length === 0) && (
                    <div className="py-32 text-center space-y-6 bg-white rounded-[3rem] border border-slate-100 shadow-sm">
                        <div className="text-7xl opacity-20">📭</div>
                        <h2 className="text-2xl font-black text-slate-900">Aucune commande</h2>
                        <p className="text-slate-500 font-medium max-w-xs mx-auto">Vos futures commandes clients apparaîtront ici pour traitement.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SellerOrdersPage;
