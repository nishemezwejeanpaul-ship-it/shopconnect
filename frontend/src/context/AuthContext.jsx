import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const loadUser = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const { data } = await api.get('/auth/me/');
            if (data.success) {
                setUser(data.data);
            }
        } catch (error) {
            console.error("Failed to load user session", error);
            // 401s are caught by api interceptor which auto-clears and redirects
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUser();
    }, []);

    const login = async (phone, password) => {
        const { data } = await api.post('/auth/login/', { phone, password });
        if (data.success) {
            localStorage.setItem('access_token', data.data.tokens.access);
            localStorage.setItem('refresh_token', data.data.tokens.refresh);
            setUser(data.data.user);
            return data.data;
        }
        return null;
    };

    const register = async (userData) => {
        const { data } = await api.post('/auth/register/', userData);
        if (data.success) {
            localStorage.setItem('access_token', data.data.tokens.access);
            localStorage.setItem('refresh_token', data.data.tokens.refresh);
            setUser(data.data.user);
            return data.data;
        }
        return null;
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout, loadUser }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
