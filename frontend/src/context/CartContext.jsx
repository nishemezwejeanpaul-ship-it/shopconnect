import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';
import { useQueryClient } from '@tanstack/react-query';

const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const { user } = useAuth();

    const fetchCart = async () => {
        if (!user) {
            setItems([]);
            setLoading(false);
            return;
        }
        try {
            const { data } = await api.get('/cart/');
            if (data.success) {
                setItems(data.data);
            }
        } catch (error) {
            console.error("Failed to fetch cart", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, [user]);

    const addItem = async (productId, quantity = 1, variantId = null) => {
        try {
            const { data } = await api.post('/cart/add/', { 
                product_id: productId, 
                quantity, 
                variant_id: variantId 
            });
            if (data.success) {
                await fetchCart(); // Refresh to get fully populated nested data
                return data.data;
            }
        } catch (error) {
            throw error.response?.data?.error || error;
        }
    };

    const updateItem = async (itemId, quantity) => {
        try {
            const { data } = await api.put(`/cart/update/${itemId}/`, { quantity });
            if (data.success) {
                await fetchCart();
                return data.data;
            }
        } catch (error) {
            throw error.response?.data?.error || error;
        }
    };

    const removeItem = async (itemId) => {
        try {
            const { data } = await api.delete(`/cart/remove/${itemId}/`);
            if (data.success) {
                setItems(prev => prev.filter(item => item.id !== itemId));
            }
        } catch (error) {
            throw error.response?.data?.error || error;
        }
    };

    const queryClient = useQueryClient();

    const clearCart = () => {
        setItems([]);
        queryClient.setQueryData(['cart'], []);
        queryClient.invalidateQueries(['cart']);
    };

    // Calculate derived state
    const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
    
    const total = items.reduce((sum, item) => {
        if (!item.product_details) return sum;
        
        let price = parseFloat(item.product_details.discount_price || item.product_details.price);
        
        // Add variant price if applicable
        if (item.variant && item.product_details.variants) {
            const variantObj = item.product_details.variants.find(v => v.id === item.variant);
            if (variantObj) {
                price += parseFloat(variantObj.additional_price || 0);
            }
        }
        
        return sum + (price * item.quantity);
    }, 0);

    return (
        <CartContext.Provider value={{ 
            items, loading, itemCount, total, 
            addItem, updateItem, removeItem, clearCart, fetchCart 
        }}>
            {children}
        </CartContext.Provider>
    );
};

export const useCart = () => useContext(CartContext);
