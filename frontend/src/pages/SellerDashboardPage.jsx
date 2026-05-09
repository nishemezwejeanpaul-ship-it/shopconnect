import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { StatsSkeleton, TableSkeleton } from '../components/SellerSkeleton';

const SellerDashboardPage = () => {
    const { data: stats, isLoading: statsLoading } = useQuery({
        queryKey: ['seller-stats'],
        queryFn: async () => {
            const { data } = await api.get('/users/seller/stats/');
            return data.data;
        }
    });

    const { data: orders, isLoading: ordersLoading } = useQuery({
        queryKey: ['seller-orders-recent'],
        queryFn: async () => {
            const { data } = await api.get('/orders/seller/orders/');
            return data.data.slice(0, 5); 
        }
    });

    if (statsLoading || ordersLoading) return (
        <div className="space-y-12">
            <StatsSkeleton />
            <TableSkeleton />
        </div>
    );

    const statCards = [
        { 
            label: 'Ventes Totales', 
            value: `${parseFloat(stats?.total_sales || 0).toLocaleString()} BIF`, 
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            ), 
            color: 'text-emerald-600',
            bg: 'bg-emerald-50'
        },
        { 
            label: 'Commandes', 
            value: stats?.total_orders || 0, 
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>
            ), 
            color: 'text-blue-600',
            bg: 'bg-blue-50'
        },
        { 
            label: 'Produits Actifs', 
            value: stats?.total_products || 0, 
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 11h.01M7 15h.01M11 7h.01M11 11h.01M11 15h.01M15 7h.01M15 11h.01M15 15h.01M19 7h.01M19 11h.01M19 15h.01M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            ), 
            color: 'text-amber-600',
            bg: 'bg-amber-50'
        },
    ];

    return (
        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {statCards.map((stat, i) => (
                    <div key={i} className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:shadow-slate-200/50 transition-all group relative overflow-hidden">
                        <div className={`absolute top-0 right-0 w-24 h-24 ${stat.bg} opacity-20 rounded-bl-[4rem] -mr-8 -mt-8 transition-transform group-hover:scale-125`}></div>
                        <div className="relative z-10">
                            <div className={`w-14 h-14 rounded-2xl ${stat.bg} ${stat.color} flex items-center justify-center mb-6 shadow-inner`}>
                                {stat.icon}
                            </div>
                            <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-2">{stat.label}</h3>
                            <p className="text-3xl font-black text-slate-900">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Recent Orders Table */}
            <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden">
                <div className="p-8 border-b border-slate-50 flex justify-between items-center bg-slate-50/30">
                    <div>
                        <h2 className="text-xl font-black text-slate-900">Commandes Récentes</h2>
                        <p className="text-sm text-slate-500 font-medium">Les 5 dernières commandes de votre boutique</p>
                    </div>
                    <Link to="/seller/orders" className="px-6 py-3 bg-white border border-slate-200 rounded-xl text-sm font-black text-slate-600 hover:bg-slate-50 transition-all shadow-sm">
                        Tout Voir
                    </Link>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-white">
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">ID Commande</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Date</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Client</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Montant</th>
                                <th className="px-8 py-5 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">Statut</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                            {orders?.map((order, idx) => (
                                <tr key={order.id} className={`${idx % 2 === 1 ? 'bg-slate-50/30' : 'bg-white'} hover:bg-emerald-50/30 transition-colors cursor-default`}>
                                    <td className="px-8 py-6 font-black text-slate-500 text-xs">#SC-{order.id.slice(-8).toUpperCase()}</td>
                                    <td className="px-8 py-6 font-bold text-slate-700 text-sm">
                                        {new Date(order.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-[10px]">👤</div>
                                            <span className="font-bold text-slate-600 text-sm">{order.shipping_address_details?.phone || 'Anonyme'}</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6 font-black text-slate-900 text-sm">{parseFloat(order.total_amount).toLocaleString()} BIF</td>
                                    <td className="px-8 py-6">
                                        <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest inline-flex items-center gap-2 ${
                                            order.status === 'completed' ? 'bg-emerald-100 text-emerald-700' : 
                                            order.status === 'pending' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'
                                        }`}>
                                            <span className={`w-1.5 h-1.5 rounded-full ${
                                                order.status === 'completed' ? 'bg-emerald-500' : 
                                                order.status === 'pending' ? 'bg-amber-500' : 'bg-blue-500'
                                            }`}></span>
                                            {order.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            {(!orders || orders.length === 0) && (
                                <tr>
                                    <td colSpan="5" className="px-8 py-20 text-center space-y-3">
                                        <div className="text-4xl grayscale opacity-20">📭</div>
                                        <p className="text-slate-400 font-bold italic">Aucune commande récente à afficher.</p>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default SellerDashboardPage;
