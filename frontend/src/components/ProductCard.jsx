import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const ProductCard = ({ product }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const imageUrl = product.main_image || 'https://placehold.co/400x400/E5E7EB/A3A3A3?text=Pas+d%27image';
  
  const hasDiscount = parseFloat(product.discount_price) > 0 && parseFloat(product.discount_price) < parseFloat(product.price);
  const displayPrice = hasDiscount ? product.discount_price : product.price;

  // Global Wishlist Query
  const { data: wishlistData } = useQuery({
    queryKey: ['wishlist'],
    queryFn: async () => {
        const { data } = await api.get('/catalog/wishlist/');
        // Handle both paginated and flat responses safely
        return data.data?.results || data.data || [];
    },
    enabled: !!user,
  });

  const wishlistItems = wishlistData || [];
  const isInWishlist = wishlistItems.some(item => item.product === product.id);

  // Optimistic Mutation
  const toggleWishlist = useMutation({
    mutationFn: async (isAdding) => {
        if (isAdding) {
            await api.post('/catalog/wishlist/add/', { product_id: product.id });
        } else {
            await api.delete(`/catalog/wishlist/remove/${product.id}/`);
        }
    },
    onMutate: async (isAdding) => {
        await queryClient.cancelQueries({ queryKey: ['wishlist'] });
        const previousWishlist = queryClient.getQueryData(['wishlist']);
        
        queryClient.setQueryData(['wishlist'], (old) => {
            const oldList = old?.results || old || [];
            if (isAdding) {
                // Add fake item
                return [{ id: 'temp', product: product.id, product_details: product }, ...oldList];
            } else {
                // Remove item
                return oldList.filter(item => item.product !== product.id);
            }
        });
        
        return { previousWishlist };
    },
    onError: (err, newTodo, context) => {
        queryClient.setQueryData(['wishlist'], context.previousWishlist);
    },
    onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ['wishlist'] });
    },
  });

  const handleWishlistClick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!user) {
          navigate('/login');
          return;
      }
      toggleWishlist.mutate(!isInWishlist);
  };

  return (
    <div className="bg-white rounded-2xl border border-border overflow-hidden flex flex-col hover:shadow-xl transition-shadow duration-300 relative">
      <div className="aspect-square bg-bg relative group">
        <img src={imageUrl} alt={product.name} className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
        
        {/* Wishlist Button */}
        <button 
            onClick={handleWishlistClick}
            className="absolute top-2 right-2 p-2 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white transition-colors shadow-sm z-10"
        >
            <svg 
                className={`w-5 h-5 transition-colors ${isInWishlist ? 'text-red-500 fill-red-500' : 'text-slate-400 fill-transparent hover:text-red-500'}`} 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                strokeWidth="2"
            >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
        </button>

        {hasDiscount && (
          <span className="absolute top-2 left-2 bg-error text-white text-xs font-bold px-2 py-1 rounded-full shadow-sm z-10">
            Promo
          </span>
        )}
      </div>
      <div className="p-4 flex flex-col flex-1">
        <span className="text-xs text-muted mb-1 font-medium">{product.shop?.name || product.shop_name || 'Boutique inconnue'}</span>
        <h3 className="text-text font-bold text-sm md:text-base line-clamp-2 mb-2 flex-1">{product.name}</h3>
        <div className="mb-4">
          <span className="text-primary font-extrabold text-lg">{parseInt(displayPrice).toLocaleString('fr-FR')} BIF</span>
          {hasDiscount && (
            <span className="text-muted line-through text-xs ml-2 block sm:inline">{parseInt(product.price).toLocaleString('fr-FR')} BIF</span>
          )}
        </div>
        <Link 
          to={`/products/${product.id}`}
          className="w-full text-center bg-primary/10 text-primary hover:bg-primary hover:text-white font-semibold py-2 rounded-xl transition-colors mt-auto"
        >
          Voir le produit
        </Link>
      </div>
    </div>
  );
};

export default ProductCard;
