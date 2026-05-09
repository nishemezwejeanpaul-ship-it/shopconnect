import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import PhoneInput, { isValidPhoneNumber } from 'react-phone-number-input';
import 'react-phone-number-input/style.css';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const loginSchema = z.object({
  password: z.string().min(1, 'Le mot de passe est requis'),
});

const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [phone, setPhone] = useState('');

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data) => {
    setErrorMsg('');
    
    if (!phone) {
      setErrorMsg('Le numéro de téléphone est requis');
      return;
    }
    
    if (!isValidPhoneNumber(phone)) {
      setErrorMsg('Numéro de téléphone invalide');
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await login(phone, data.password);
      if (result) {
        navigate('/');
      } else {
        setErrorMsg("Numéro de téléphone ou mot de passe incorrect.");
      }
    } catch (err) {
      setErrorMsg(err?.response?.data?.error?.message || "Une erreur inattendue s'est produite.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gradient-to-br from-bg to-primary/10 p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-border transition-all duration-300 hover:shadow-2xl">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-extrabold text-text mb-2">Bienvenue</h2>
          <p className="text-muted">Connectez-vous à votre compte ShopConnect</p>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-error/30 text-error text-sm flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" /></svg>
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-text mb-2">Numéro de téléphone</label>
            <PhoneInput
              defaultCountry="BI"
              value={phone}
              onChange={setPhone}
              placeholder="Ex: +257 61 000 000"
              className="w-full px-4 py-3 rounded-xl border border-border bg-bg focus-within:ring-2 focus-within:ring-primary transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-text mb-2">Mot de passe</label>
            <input
              type="password"
              {...register('password')}
              placeholder="••••••••"
              className={`w-full px-4 py-3 rounded-xl border ${errors.password ? 'border-error bg-red-50' : 'border-border bg-bg'} focus:outline-none focus:ring-2 focus:ring-primary transition-colors`}
            />
            {errors.password && <p className="mt-2 text-sm text-error">{errors.password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-3 px-4 rounded-xl transition-all duration-200 flex justify-center items-center disabled:opacity-70 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
          >
            {isSubmitting ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-muted text-sm">
            Vous n'avez pas de compte ?{' '}
            <Link to="/register" className="text-primary font-bold hover:text-primary-dark transition-colors">
              Créer un compte
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
