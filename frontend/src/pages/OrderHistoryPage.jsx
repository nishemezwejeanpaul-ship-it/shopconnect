import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

const OrderHistoryPage = () => {
    const { data: orders, isLoading, isError } = useQuery({
        queryKey: ['orders'],
        queryFn: async () => {
            const { data } = await api.get('/orders/');
            return data.data;
        }
    });

    const getStatusConfig = (status) => {
        const configs = {
            pending: { label: 'En attente', color: 'bg-amber-100 text-amber-700 border-amber-200' },
            confirmed: { label: 'Confirmée', color: 'bg-blue-100 text-blue-700 border-blue-200' },
            completed: { label: 'Terminée', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
            cancelled: { label: 'Annulée', color: 'bg-red-100 text-red-700 border-red-200' }
        };
        return configs[status] || configs.pending;
    };

    if (isLoading) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-12 space-y-4">
                {[1, 2, 3].map(i => (
                    <div key={i} className="h-32 bg-slate-100 animate-pulse rounded-3xl"></div>
                ))}
            </div>
        );
    }

    if (isError) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-24 text-center">
                <p className="text-slate-500 font-bold">Impossible de charger vos commandes.</p>
            </div>
        );
    }

    if (!orders || orders.length === 0) {
        return (
            <div className="max-w-4xl mx-auto px-4 py-24 text-center space-y-6">
                <div className="text-6xl">📦</div>
                <h2 className="text-2xl font-black text-slate-900">Vous n'avez pas encore de commande</h2>
                <p className="text-slate-500">Découvrez nos produits et passez votre première commande !</p>
                <Link to="/catalog" className="inline-block px-8 py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-xl shadow-emerald-600/20">
                    Aller au catalogue
                </Link>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-4 py-12">
            <h1 className="text-3xl font-black text-slate-900 mb-8">Mes Commandes</h1>
            <div className="space-y-4">
                {orders.map(order => {
                    const status = getStatusConfig(order.status);
                    return (
                        <Link 
                            key={order.id} 
                            to={`/orders/${order.id}`}
                            className="block p-6 bg-white border border-slate-100 rounded-3xl hover:border-emerald-300 hover:shadow-xl hover:shadow-emerald-600/5 transition-all group"
                        >
                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-3">
                                        <span className="text-sm font-black text-slate-400 uppercase tracking-widest">#SC-{order.id.slice(-8).toUpperCase()}</span>
                                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${status.color}`}>
                                            {status.label}
                                        </span>
                                    </div>
                                    <h3 className="font-bold text-slate-900">
                                        {new Date(order.created_at).toLocaleDateString('fr-FR', {
                                            day: 'numeric', month: 'long', year: 'numeric'
                                        })}
                                    </h3>
                                    <p className="text-sm text-slate-500">
                                        {order.items?.length || 0} {order.items?.length > 1 ? 'articles' : 'article'}
                                    </p>
                                </div>
                                <div className="flex items-center justify-between md:text-right">
                                    <div>
                                        <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Total</p>
                                        <p className="text-xl font-black text-emerald-600">
                                            {parseFloat(order.total_amount).toLocaleString()} BIF
                                        </p>
                                    </div>
                                    <div className="md:hidden">
                                        <span className="text-emerald-500">→</span>
                                    </div>
                                </div>
                            </div>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
};

export default OrderHistoryPage;
