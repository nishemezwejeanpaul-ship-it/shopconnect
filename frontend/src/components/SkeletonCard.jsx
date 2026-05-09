import React from 'react';

const SkeletonCard = () => {
  return (
    <div className="bg-white rounded-2xl border border-border overflow-hidden flex flex-col animate-pulse">
      <div className="aspect-square bg-slate-200" />
      <div className="p-4 flex flex-col flex-1">
        <div className="h-3 bg-slate-200 rounded w-1/3 mb-2" />
        <div className="h-4 bg-slate-200 rounded w-3/4 mb-1" />
        <div className="h-4 bg-slate-200 rounded w-1/2 mb-4" />
        <div className="h-6 bg-slate-200 rounded w-1/3 mb-4" />
        <div className="h-10 bg-slate-200 rounded-xl w-full mt-auto" />
      </div>
    </div>
  );
};

export default SkeletonCard;
