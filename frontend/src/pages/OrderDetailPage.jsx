import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

const OrderDetailPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    // Fetch current order
    const { data: order, isLoading, isError } = useQuery({
        queryKey: ['order', id],
        queryFn: async () => {
            const { data } = await api.get(`/orders/${id}/`);
            return data.data;
        }
    });

    // Fetch all orders for navigation
    const { data: allOrders } = useQuery({
        queryKey: ['orders'],
        queryFn: async () => {
            const { data } = await api.get('/orders/');
            return data.data;
        }
    });

    if (isLoading) return <div className="max-w-6xl mx-auto p-12 text-center font-bold text-slate-400">Chargement...</div>;
    if (isError || !order) return <div className="max-w-6xl mx-auto p-12 text-center text-red-500 font-bold">Commande introuvable</div>;

    // Navigation Logic
    const ordersList = allOrders || [];
    const currentIndex = ordersList.findIndex(o => o.id === id);
    const hasPrevious = currentIndex > 0;
    const hasNext = currentIndex < ordersList.length - 1 && currentIndex !== -1;

    const isCOD = order.payment_details?.method === 'cash';
    const isPaid = order.payment_details?.status === 'paid';

    const getStatusConfig = (status) => {
        const configs = {
            pending: { label: 'En attente', color: 'bg-amber-100 text-amber-700 border-amber-200' },
            confirmed: { label: 'Confirmée', color: 'bg-blue-100 text-blue-700 border-blue-200' },
            completed: { label: 'Terminée', color: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
            cancelled: { label: 'Annulée', color: 'bg-red-100 text-red-700 border-red-200' }
        };
        return configs[status] || configs.pending;
    };

    const steps = [
        { key: 'received', label: 'Commande', icon: '✓', date: new Date(order.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }) },
        { 
            key: 'paid', 
            label: 'Paiement', 
            icon: isPaid ? '✓' : (isCOD ? '🤝' : '$'),
            date: isPaid ? new Date(order.payment_details.paid_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }) : (isCOD ? 'À la réception' : 'En attente')
        },
        { key: 'processing', label: 'Prépa', icon: '📦', date: order.status === 'confirmed' ? 'En cours' : '—' },
        { key: 'shipping', label: 'Livraison', icon: '🚚', date: order.status === 'shipping' ? 'En cours' : '—' },
        { key: 'delivered', label: 'Livré', icon: '✓', date: order.status === 'completed' ? 'Terminé' : '—' }
    ];

    const getStepIndex = (status) => {
        if (status === 'completed') return 4;
        if (status === 'shipping') return 3;
        if (status === 'confirmed') return 2;
        if (isPaid) return 1;
        if (isCOD && status !== 'pending') return 1;
        return 0;
    };

    const currentStep = getStepIndex(order.status);
    const statusInfo = getStatusConfig(order.status);

    // Group items by shop for the breakdown
    const shopBreakdown = order.items?.reduce((acc, item) => {
        const shopName = item.product_details?.shop_name || 'Boutique';
        if (!acc[shopName]) acc[shopName] = 0;
        acc[shopName] += parseFloat(item.total_price);
        return acc;
    }, {}) || {};

    return (
        <div className="max-w-6xl mx-auto px-4 py-8 space-y-8 font-sans text-slate-900 bg-slate-50/30 min-h-screen">
            {/* Header */}
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <Link to="/orders" className="inline-flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-slate-900 transition-colors">
                        <span className="text-lg">←</span> Mes Commandes
                    </Link>
                    
                    {/* Order Navigation */}
                    {ordersList.length > 0 && (
                        <div className="flex items-center gap-2">
                            {hasPrevious && (
                                <button 
                                    onClick={() => navigate(`/orders/${ordersList[currentIndex - 1].id}`)}
                                    className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-[#16A34A] hover:text-[#16A34A] transition-all"
                                >
                                    ‹
                                </button>
                            )}
                            <span className="text-xs font-black text-slate-400 px-2 min-w-[40px] text-center">
                                {currentIndex + 1} / {ordersList.length}
                            </span>
                            {hasNext && (
                                <button 
                                    onClick={() => navigate(`/orders/${ordersList[currentIndex + 1].id}`)}
                                    className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-400 hover:border-[#16A34A] hover:text-[#16A34A] transition-all"
                                >
                                    ›
                                </button>
                            )}
                        </div>
                    )}
                </div>

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">Commande #SC-{order.id.slice(-8).toUpperCase()}</h1>
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${statusInfo.color}`}>
                            {statusInfo.label}
                        </span>
                    </div>
                    <p className="text-slate-400 font-bold text-sm">
                        Passée le {new Date(order.created_at).toLocaleTimeString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' }).replace(':', 'h')}
                    </p>
                </div>
            </div>

            {/* Timeline Card */}
            <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm overflow-x-auto">
                <div className="flex justify-between min-w-[700px] relative px-4">
                    <div className="absolute top-5 left-10 right-10 h-[2px] bg-slate-100 -z-0"></div>
                    <div className="absolute top-5 left-10 h-[2px] bg-[#16A34A] -z-0 transition-all duration-1000" style={{ width: `${Math.max(0, (currentStep / (steps.length - 1)) * 100 - 5)}%` }}></div>
                    
                    {steps.map((step, idx) => {
                        const isCompleted = idx < currentStep;
                        const isCurrent = idx === currentStep;
                        const isFuture = idx > currentStep;

                        return (
                            <div key={step.key} className="relative z-10 flex flex-col items-center gap-4">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-black transition-all duration-500 
                                    ${isCompleted ? 'bg-[#16A34A] text-white' : 
                                      isCurrent ? 'bg-white border-[3px] border-[#16A34A] text-[#16A34A] shadow-[0_0_0_4px_#DCFCE7]' : 
                                      'bg-white border-[3px] border-slate-100 text-slate-200'}`}>
                                    {step.icon}
                                </div>
                                <div className="text-center">
                                    <p className={`text-[11px] font-black uppercase tracking-widest mb-1 ${isFuture ? 'text-slate-300' : 'text-[#16A34A]'}`}>
                                        {step.label}
                                    </p>
                                    <p className={`text-[10px] font-bold ${isFuture ? 'text-slate-200' : 'text-slate-400'}`}>
                                        {step.date}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                {/* Left Column (60%) */}
                <div className="lg:col-span-3 space-y-8">
                    {/* Articles Section */}
                    <div className="space-y-4">
                        <h2 className="flex items-center gap-2 text-lg font-black text-slate-900 px-2">
                            <span>📦</span> Articles
                        </h2>
                        <div className="bg-white rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden divide-y divide-slate-50">
                            {order.items?.map(item => (
                                <div key={item.id} className="p-6 flex items-start gap-4 hover:bg-slate-50/50 transition-colors">
                                    <div className="w-14 h-14 bg-slate-50 rounded-xl overflow-hidden border border-slate-100 flex-shrink-0">
                                        <img src={item.product_details?.main_image || 'https://placehold.co/56x56'} alt="" className="w-full h-full object-cover" />
                                    </div>
                                    <div className="flex-1 space-y-1">
                                        <h3 className="font-black text-slate-900 text-base leading-tight">{item.product_details?.name}</h3>
                                        <div className="flex flex-wrap gap-x-3 gap-y-1">
                                            <p className="text-[11px] font-bold text-slate-400 flex items-center gap-1">
                                                <span>🏪</span> {item.product_details?.shop_name}
                                            </p>
                                            {item.variant && (
                                                <p className="text-[11px] font-bold text-slate-400">Variante: {item.variant_details?.name || 'Standard'}</p>
                                            )}
                                            <p className="text-[11px] font-bold text-slate-400">Quantité: {item.quantity}</p>
                                        </div>
                                    </div>
                                    <div className="text-right flex-shrink-0">
                                        <p className="font-black text-[#16A34A] text-lg">
                                            {parseFloat(item.total_price).toLocaleString()} <span className="text-[10px] opacity-60">BIF</span>
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Livraison Section */}
                    <div className="space-y-4">
                        <h2 className="flex items-center gap-2 text-lg font-black text-slate-900 px-2">
                            <span>🚚</span> Livraison
                        </h2>
                        <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm space-y-6">
                            <div className="inline-flex px-4 py-1.5 bg-emerald-50 text-[#16A34A] rounded-full text-xs font-black uppercase tracking-widest">
                                {order.pickup_point ? 'Retrait en Point Relais' : 'Livraison à domicile'}
                            </div>
                            
                            <div className="bg-slate-50/80 p-6 rounded-2xl border border-slate-100">
                                <p className="font-black text-slate-900 text-base mb-2">
                                    {order.pickup_point ? order.pickup_point_details?.name : 'Adresse de destination'}
                                </p>
                                <p className="text-sm font-bold text-slate-500 leading-relaxed">
                                    {order.pickup_point ? order.pickup_point_details?.address : order.shipping_address_details?.address}
                                    <br />
                                    Contact: {order.shipping_address_details?.phone}
                                </p>
                            </div>

                            <div className="flex items-center gap-4 py-4 border-t border-slate-50">
                                <div className="w-10 h-10 bg-slate-50 rounded-full flex items-center justify-center text-lg shadow-inner">
                                    {isCOD ? '🤝' : '📱'}
                                </div>
                                <div>
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Mode de paiement</p>
                                    <p className="font-black text-slate-900">{isCOD ? 'Paiement à la Livraison' : 'Mobile Money'}</p>
                                </div>
                            </div>

                            <button className="w-full py-4 bg-slate-900 text-white font-black rounded-2xl hover:bg-slate-800 transition-all text-sm shadow-xl shadow-slate-900/10">
                                Besoin d'aide avec cette commande ?
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Column (40%) */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Summary Card */}
                    <div className="bg-gradient-to-br from-[#16A34A] to-[#15803D] p-8 rounded-[2.5rem] shadow-2xl shadow-emerald-900/20 text-white space-y-5">
                        <div className="flex justify-between text-sm font-bold opacity-80">
                            <span>Sous-total</span>
                            <span>{parseFloat(order.subtotal).toLocaleString()} BIF</span>
                        </div>
                        <div className="flex justify-between text-sm font-bold opacity-80">
                            <span>Livraison</span>
                            <span>{parseFloat(order.shipping_fee) > 0 ? `${parseFloat(order.shipping_fee).toLocaleString()} BIF` : 'Gratuit'}</span>
                        </div>
                        <div className="flex justify-between text-sm font-bold opacity-80">
                            <span>Réductions</span>
                            <span>— {parseFloat(order.discount_amount || 0).toLocaleString()} BIF</span>
                        </div>
                        <div className="pt-5 border-t border-white/20 flex justify-between items-center">
                            <span className="text-lg font-black">Total</span>
                            <span className="text-3xl font-black">{parseFloat(order.total_amount).toLocaleString()} <span className="text-xs opacity-60">BIF</span></span>
                        </div>
                    </div>

                    {/* Per-Shop Breakdown */}
                    <div className="bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm space-y-4">
                        <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Par boutique</h3>
                        <div className="space-y-4">
                            {Object.entries(shopBreakdown).map(([shop, total]) => (
                                <div key={shop} className="space-y-3">
                                    <div className="flex justify-between items-center">
                                        <p className="font-black text-slate-900 text-sm">{shop}</p>
                                        <p className="font-black text-slate-900">{total.toLocaleString()} BIF</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-tighter border ${statusInfo.color}`}>
                                            {statusInfo.label}
                                        </span>
                                    </div>
                                    <hr className="border-slate-50 last:hidden" />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Support Amber Card */}
                    <div className="bg-amber-50 p-8 rounded-[2rem] border border-amber-100 space-y-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center text-lg">💡</div>
                            <h3 className="font-black text-amber-900 text-lg leading-tight">Besoin d'aide ?</h3>
                        </div>
                        <p className="text-sm font-bold text-amber-700/80 leading-relaxed">
                            Une question sur votre commande ou un problème de livraison ? Notre équipe est là pour vous.
                        </p>
                        <button className="w-full py-4 bg-amber-500 text-white font-black rounded-2xl hover:bg-amber-600 transition-all text-sm shadow-lg shadow-amber-500/20">
                            Nous contacter
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OrderDetailPage;
