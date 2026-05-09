import React from 'react';

export const StatsSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white p-8 rounded-[2.5rem] border border-slate-100 shadow-sm animate-pulse">
                <div className="w-14 h-14 rounded-2xl bg-slate-100 mb-6"></div>
                <div className="h-4 bg-slate-100 rounded w-1/2 mb-2"></div>
                <div className="h-8 bg-slate-100 rounded w-3/4"></div>
            </div>
        ))}
    </div>
);

export const TableSkeleton = () => (
    <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-sm overflow-hidden animate-pulse">
        <div className="p-8 border-b border-slate-50">
            <div className="h-6 bg-slate-100 rounded w-1/4 mb-2"></div>
            <div className="h-4 bg-slate-100 rounded w-1/3"></div>
        </div>
        <div className="p-8 space-y-4">
            {[...Array(5)].map((_, i) => (
                <div key={i} className="flex gap-4">
                    <div className="h-10 bg-slate-50 rounded flex-1"></div>
                    <div className="h-10 bg-slate-50 rounded flex-1"></div>
                    <div className="h-10 bg-slate-50 rounded flex-1"></div>
                </div>
            ))}
        </div>
    </div>
);

export const ProductGridSkeleton = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
        {[...Array(8)].map((_, i) => (
            <div key={i} className="bg-white p-4 rounded-2xl border border-slate-100">
                <div className="aspect-square bg-slate-100 rounded-xl mb-4"></div>
                <div className="h-4 bg-slate-100 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-slate-100 rounded w-1/2"></div>
            </div>
        ))}
    </div>
);
