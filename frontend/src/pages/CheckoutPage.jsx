import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import api from '../services/api';

const CheckoutPage = () => {
    const { items, total, clearCart, loading, fetchCart } = useCart();
    const navigate = useNavigate();
    
    const [step, setStep] = useState(1);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isFinishing, setIsFinishing] = useState(false);
    const [error, setError] = useState('');

    // Data from API
    const [allRegions, setAllRegions] = useState([]);
    const [parentRegions, setParentRegions] = useState([]);
    const [pickupPoints, setPickupPoints] = useState([]);
    
    // Selection State
    const [selectedParentId, setSelectedParentId] = useState('');
    const [selectedRegionId, setSelectedRegionId] = useState('');
    const [selectedMethod, setSelectedMethod] = useState(null);
    const [selectedPickupPointId, setSelectedPickupPointId] = useState('');
    
    // Calculations for Step 1
    const [calculations, setCalculations] = useState({
        DOOR_FREE: { loading: false, data: null },
        DOOR_EXPRESS: { loading: false, data: null },
        PICKUP_FREE: { loading: false, data: null }
    });

    // Step 2 State (Address)
    const [addressInfo, setAddressInfo] = useState({
        fullName: '',
        phone: '+257',
        addressText: ''
    });

    // Step 3 State
    const [paymentMethod, setPaymentMethod] = useState('mobile_money');
    const [paymentPhone, setPaymentPhone] = useState('');

    useEffect(() => {
        if (!loading && !isFinishing && (!items || items.length === 0)) {
            navigate('/cart');
        }
    }, [loading, items, navigate, isFinishing]);

    useEffect(() => {
        if (items && items.length > 0) {
            fetchInitialData();
        }
    }, [items]);

    const fetchInitialData = async () => {
        try {
            const [regRes, pickRes] = await Promise.all([
                api.get('/regions/'),
                api.get('/pickup-points/')
            ]);
            const rawRegions = regRes.data.data;
            setAllRegions(rawRegions);
            setParentRegions(rawRegions.filter(r => !r.parent));
            setPickupPoints(pickRes.data.data);
        } catch (err) {
            console.error("Fetch failed", err);
        }
    };

    // Calculate all 3 methods when the final region changes
    useEffect(() => {
        if (selectedRegionId) {
            runAllCalculations();
        } else {
            // Reset calculations if region cleared
            setCalculations({
                DOOR_FREE: { loading: false, data: null },
                DOOR_EXPRESS: { loading: false, data: null },
                PICKUP_FREE: { loading: false, data: null }
            });
            setSelectedMethod(null);
        }
    }, [selectedRegionId]);

    const runAllCalculations = async () => {
        const methods = ['DOOR_FREE', 'DOOR_EXPRESS', 'PICKUP_FREE'];
        setCalculations(prev => {
            const next = { ...prev };
            methods.forEach(m => next[m] = { ...next[m], loading: true, data: null });
            return next;
        });

        methods.forEach(async (code) => {
            try {
                const res = await api.post('/orders/calculate-shipping/', {
                    delivery_method_code: code,
                    to_region_id: selectedRegionId,
                    pickup_point_id: code === 'PICKUP_FREE' ? (pickupPoints.find(p => String(p.region) === String(selectedRegionId))?.id || pickupPoints[0]?.id) : null
                });
                setCalculations(prev => ({
                    ...prev,
                    [code]: { loading: false, data: res.data.data }
                }));
            } catch (err) {
                setCalculations(prev => ({
                    ...prev,
                    [code]: { loading: false, data: { available: false } }
                }));
            }
        });
    };

    const handleConfirm = async () => {
        if (!items || items.length === 0) {
            setError("Votre panier est vide.");
            return;
        }
        setIsProcessing(true);
        setError('');

        try {
            const addrRes = await api.post('/shipping-addresses/', {
                region: selectedRegionId,
                label: 'Commande Directe',
                address: addressInfo.addressText || 'Retrait en point relais',
                phone: addressInfo.phone || paymentPhone,
                is_default: false
            });
            const addressId = addrRes.data.data.id;

            const orderRes = await api.post('/orders/create/', {
                delivery_method_code: selectedMethod.code,
                shipping_address_id: addressId,
                pickup_point_id: selectedMethod.code === 'PICKUP_FREE' ? selectedPickupPointId : null
            });
            const order = orderRes.data.data;

            setIsFinishing(true);
            clearCart();

            await api.post('/payments/initiate/', {
                order_id: order.id,
                method: paymentMethod === 'cod' ? 'cash' : 'mobile_money'
            });

            navigate(`/orders/${order.id}`, { replace: true });
        } catch (err) {
            const errorMsg = err.response?.data?.error?.message || "Une erreur est survenue.";
            setError(errorMsg);
            if (err.response?.data?.error?.code === 'EMPTY_CART') {
                clearCart();
            }
        } finally {
            setIsProcessing(false);
        }
    };

    const renderStep1 = () => {
        const subRegions = allRegions.filter(r => r.parent === selectedParentId);
        const hasSubRegions = subRegions.length > 0;

        return (
            <div className="space-y-8 animate-in fade-in duration-500">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-bold text-slate-700 mb-3">Province / Ville</label>
                        <select 
                            value={selectedParentId}
                            onChange={(e) => {
                                setSelectedParentId(e.target.value);
                                setSelectedRegionId(''); // Reset child
                                setSelectedMethod(null);
                            }}
                            className="w-full p-4 rounded-2xl border-2 border-emerald-100 bg-white focus:border-emerald-500 transition-all outline-none font-medium"
                        >
                            <option value="">-- Choisir --</option>
                            {parentRegions.map(r => (
                                <option key={r.id} value={r.id}>{r.name}</option>
                            ))}
                        </select>
                    </div>

                    {hasSubRegions && (
                        <div className="animate-in slide-in-from-left-4 duration-300">
                            <label className="block text-sm font-bold text-slate-700 mb-3">Quartier / Zone</label>
                            <select 
                                value={selectedRegionId}
                                onChange={(e) => {
                                    setSelectedRegionId(e.target.value);
                                    setSelectedMethod(null);
                                }}
                                className="w-full p-4 rounded-2xl border-2 border-emerald-100 bg-white focus:border-emerald-500 transition-all outline-none font-medium"
                            >
                                <option value="">-- Choisir --</option>
                                {subRegions.map(r => (
                                    <option key={r.id} value={r.id}>{r.name}</option>
                                ))}
                            </select>
                        </div>
                    )}
                </div>

                {/* If the parent has NO sub-regions, it acts as the final region itself */}
                {!hasSubRegions && selectedParentId && !selectedRegionId && (
                    <div className="flex justify-center">
                        <button 
                            onClick={() => setSelectedRegionId(selectedParentId)}
                            className="px-6 py-2 bg-emerald-100 text-emerald-700 rounded-full font-bold text-sm hover:bg-emerald-200 transition-colors"
                        >
                            Confirmer "{parentRegions.find(p => p.id === selectedParentId)?.name}" comme destination
                        </button>
                    </div>
                )}

                {selectedRegionId && (
                    <div className="space-y-4">
                        <label className="block text-sm font-bold text-slate-700 mb-2">Modes de livraison pour {allRegions.find(r => r.id === selectedRegionId)?.name}</label>
                        <div className="grid grid-cols-1 gap-4">
                            {['DOOR_FREE', 'DOOR_EXPRESS', 'PICKUP_FREE'].map((code) => {
                                const calc = calculations[code];
                                const isAvailable = calc.data?.available;
                                const isSelected = selectedMethod?.code === code;
                                
                                const icons = { DOOR_FREE: '🏠', DOOR_EXPRESS: '⚡', PICKUP_FREE: '🏪' };
                                const colors = { DOOR_FREE: 'emerald', DOOR_EXPRESS: 'amber', PICKUP_FREE: 'blue' };

                                return (
                                    <div 
                                        key={code}
                                        onClick={() => isAvailable && setSelectedMethod({ code, ...calc.data })}
                                        className={`p-5 rounded-2xl border-2 transition-all cursor-pointer ${
                                            isSelected 
                                            ? 'border-emerald-500 bg-emerald-50 shadow-md' 
                                            : isAvailable 
                                                ? 'border-slate-100 bg-white hover:border-emerald-200' 
                                                : 'border-slate-50 bg-slate-50 opacity-60 grayscale cursor-not-allowed'
                                        }`}
                                    >
                                        <div className="flex justify-between items-start">
                                            <div className="flex gap-4">
                                                <div className={`w-12 h-12 bg-${colors[code]}-100 rounded-full flex items-center justify-center text-xl`}>
                                                    {icons[code]}
                                                </div>
                                                <div>
                                                    <h3 className="font-bold text-slate-900">{calc.data?.method_name || (code === 'DOOR_FREE' ? 'Livraison à domicile' : code === 'DOOR_EXPRESS' ? 'Livraison Express' : 'Retrait en Point Relais')}</h3>
                                                    <p className="text-sm text-slate-500">
                                                        {code === 'DOOR_FREE' ? 'Standard (24-48h)' : code === 'DOOR_EXPRESS' ? 'Aujourd\'hui (2-4h)' : 'Estimation: 2-3 jours'}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <span className="font-black text-emerald-600">
                                                    {calc.loading ? '...' : (calc.data?.shipping_fee > 0 ? `${parseFloat(calc.data.shipping_fee).toLocaleString()} BIF` : 'Gratuit')}
                                                </span>
                                            </div>
                                        </div>
                                        {!isAvailable && !calc.loading && calc.data && (
                                            <p className="mt-3 text-xs font-bold text-amber-600 italic">Non disponible dans cette zone</p>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {selectedMethod?.code === 'PICKUP_FREE' && (
                    <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 animate-in slide-in-from-top-4 duration-300">
                        <label className="block text-sm font-bold text-slate-700 mb-3">Choisir le point de retrait</label>
                        {pickupPoints.filter(p => String(p.region) === String(selectedRegionId)).length > 0 ? (
                            <select 
                                value={selectedPickupPointId}
                                onChange={(e) => setSelectedPickupPointId(e.target.value)}
                                className="w-full p-3 rounded-xl border border-slate-200 bg-white font-medium outline-none focus:ring-2 focus:ring-emerald-500/20"
                            >
                                <option value="">-- Sélectionner un point --</option>
                                {pickupPoints.filter(p => String(p.region) === String(selectedRegionId)).map(p => (
                                    <option key={p.id} value={p.id}>{p.name} - {p.address}</option>
                                ))}
                            </select>
                        ) : (
                            <p className="text-sm font-bold text-amber-600 bg-amber-50 p-3 rounded-xl border border-amber-100 italic">
                                ⚠️ Aucun point de retrait disponible ici pour le moment.
                            </p>
                        )}
                    </div>
                )}

                <button 
                    disabled={!selectedMethod || (selectedMethod.code === 'PICKUP_FREE' && !selectedPickupPointId)}
                    onClick={() => setStep(selectedMethod.code === 'PICKUP_FREE' ? 3 : 2)}
                    className="w-full py-5 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-2xl shadow-xl shadow-emerald-600/20 transition-all disabled:opacity-50 disabled:shadow-none text-lg"
                >
                    Continuer
                </button>
            </div>
        );
    };

    const renderStep2 = () => (
        <div className="space-y-6 animate-in slide-in-from-right-8 duration-500">
            <h2 className="text-2xl font-black text-slate-900">Détails de l'adresse</h2>
            <div className="space-y-4">
                <div>
                    <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Nom complet</label>
                    <input 
                        type="text"
                        value={addressInfo.fullName}
                        onChange={(e) => setAddressInfo({...addressInfo, fullName: e.target.value})}
                        className="w-full p-4 rounded-xl bg-slate-50 border-2 border-slate-100 focus:border-emerald-500 outline-none transition-all"
                        placeholder="Jean Dupont"
                    />
                </div>
                <div>
                    <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Téléphone</label>
                    <input 
                        type="tel"
                        value={addressInfo.phone}
                        onChange={(e) => setAddressInfo({...addressInfo, phone: e.target.value})}
                        className="w-full p-4 rounded-xl bg-slate-50 border-2 border-slate-100 focus:border-emerald-500 outline-none transition-all font-mono"
                        placeholder="+257 ...."
                    />
                </div>
                <div>
                    <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Adresse précise (Rue, n° maison...)</label>
                    <textarea 
                        rows="3"
                        value={addressInfo.addressText}
                        onChange={(e) => setAddressInfo({...addressInfo, addressText: e.target.value})}
                        className="w-full p-4 rounded-xl bg-slate-50 border-2 border-slate-100 focus:border-emerald-500 outline-none transition-all"
                        placeholder="Avenue de l'indépendance, n° 15..."
                    ></textarea>
                </div>
            </div>

            <div className="flex gap-4">
                <button onClick={() => setStep(1)} className="flex-1 py-4 font-bold text-slate-500 hover:text-slate-900 transition-colors">Retour</button>
                <button 
                    disabled={!addressInfo.fullName || !addressInfo.phone || !addressInfo.addressText}
                    onClick={() => setStep(3)}
                    className="flex-[2] py-4 bg-emerald-600 text-white font-black rounded-2xl shadow-lg shadow-emerald-600/20 disabled:opacity-50"
                >
                    Récapitulatif
                </button>
            </div>
        </div>
    );

    const renderStep3 = () => (
        <div className="space-y-8 animate-in slide-in-from-bottom-8 duration-500">
            <div className="bg-white border-2 border-slate-100 rounded-3xl p-8 shadow-sm space-y-6">
                <h2 className="text-xl font-black text-slate-900 border-b-2 border-slate-50 pb-4">Résumé de la commande</h2>
                <div className="space-y-4">
                    {items.map(item => (
                        <div key={item.id} className="flex justify-between items-center text-sm font-medium">
                            <span className="text-slate-600">{item.quantity}x {item.product_details.name}</span>
                            <span className="text-slate-900">{(item.product_details.price * item.quantity).toLocaleString()} BIF</span>
                        </div>
                    ))}
                </div>
                <div className="pt-6 border-t-2 border-slate-50 space-y-3">
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Sous-total</span>
                        <span className="font-bold text-slate-700">{total.toLocaleString()} BIF</span>
                    </div>
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-500">Livraison ({selectedMethod.name})</span>
                        <span className="font-bold text-emerald-600">{selectedMethod.shipping_fee > 0 ? `${parseFloat(selectedMethod.shipping_fee).toLocaleString()} BIF` : 'Gratuit'}</span>
                    </div>
                    <div className="flex justify-between items-center pt-4">
                        <span className="text-lg font-black text-slate-900">Total à payer</span>
                        <span className="text-2xl font-black text-emerald-600">{(total + parseFloat(selectedMethod.shipping_fee || 0)).toLocaleString()} BIF</span>
                    </div>
                </div>
            </div>

            <div className="space-y-4">
                <label className="block text-sm font-black text-slate-700 uppercase tracking-wider">Mode de paiement</label>
                <div className="grid grid-cols-2 gap-4">
                    <button 
                        onClick={() => setPaymentMethod('mobile_money')}
                        className={`p-4 rounded-2xl border-2 transition-all font-bold ${paymentMethod === 'mobile_money' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-slate-100 bg-white text-slate-400'}`}
                    >
                        Mobile Money
                    </button>
                    <button 
                        onClick={() => setPaymentMethod('cod')}
                        className={`p-4 rounded-2xl border-2 transition-all font-bold ${paymentMethod === 'cod' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-slate-100 bg-white text-slate-400'}`}
                    >
                        Cash on Delivery
                    </button>
                </div>

                {paymentMethod === 'mobile_money' && (
                    <div className="bg-slate-50 p-6 rounded-2xl border-2 border-slate-100 animate-in fade-in duration-300">
                        <label className="block text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Numéro Lumicash / Ecocash</label>
                        <input 
                            type="tel"
                            value={paymentPhone}
                            onChange={(e) => setPaymentPhone(e.target.value)}
                            className="w-full p-4 rounded-xl border-2 border-slate-100 focus:border-emerald-500 outline-none font-mono text-lg"
                            placeholder="6x .. .. .."
                        />
                    </div>
                )}
            </div>

            {error && (
                <div className="p-4 bg-red-50 border-2 border-red-100 text-red-600 rounded-2xl text-sm font-bold text-center">
                    {error}
                </div>
            )}

            <div className="flex gap-4">
                <button onClick={() => setStep(selectedMethod.code === 'PICKUP_FREE' ? 1 : 2)} className="flex-1 py-4 font-bold text-slate-500">Retour</button>
                <button 
                    disabled={isProcessing || (paymentMethod === 'mobile_money' && !paymentPhone)}
                    onClick={handleConfirm}
                    className="flex-[2] py-5 bg-emerald-600 hover:bg-emerald-700 text-white font-black rounded-3xl shadow-2xl shadow-emerald-600/30 text-lg transition-transform active:scale-95"
                >
                    {isProcessing ? "Traitement..." : "Confirmer la commande"}
                </button>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-50/30 py-12 px-4 font-sans text-slate-900">
            <div className="max-w-3xl mx-auto">
                {/* Progress Header */}
                <div className="flex items-center justify-between mb-16 relative">
                    <div className="absolute top-1/2 left-0 w-full h-1 bg-slate-100 -translate-y-1/2 z-0"></div>
                    <div className={`absolute top-1/2 left-0 h-1 bg-emerald-500 -translate-y-1/2 transition-all duration-500 z-0`} style={{ width: `${(step - 1) * 50}%` }}></div>
                    {[1, 2, 3].map((s) => (
                        <div key={s} className="relative z-10 flex flex-col items-center gap-3">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center font-black transition-all duration-500 ${step >= s ? 'bg-emerald-600 text-white shadow-xl shadow-emerald-600/30' : 'bg-white border-4 border-slate-100 text-slate-300'}`}>
                                {s}
                            </div>
                            <span className={`text-[10px] font-black uppercase tracking-widest ${step >= s ? 'text-emerald-700' : 'text-slate-300'}`}>
                                {s === 1 ? 'Livraison' : s === 2 ? 'Adresse' : 'Paiement'}
                            </span>
                        </div>
                    ))}
                </div>

                <div className="bg-white/40 backdrop-blur-xl border border-white/20 p-2 rounded-[2rem]">
                    <div className="bg-white rounded-[1.8rem] p-8 shadow-2xl shadow-slate-200/50">
                        {step === 1 && renderStep1()}
                        {step === 2 && renderStep2()}
                        {step === 3 && renderStep3()}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CheckoutPage;
