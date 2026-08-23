import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  label?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  label,
  className = '',
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-10 h-10 border-3',
    xl: 'w-16 h-16 border-4',
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <div className="relative">
        <div
          className={`${sizeClasses[size]} rounded-full border-primary-500/20 border-t-primary-500 animate-spin`}
        />
        <div
          className={`absolute inset-0 ${sizeClasses[size]} rounded-full border-accent-cyan/10 border-b-accent-cyan animate-spin`}
          style={{ animationDirection: 'reverse', animationDuration: '1.2s' }}
        />
      </div>
      {label && (
        <p className="text-xs text-slate-400 font-medium tracking-wide animate-pulse">
          {label}
        </p>
      )}
    </div>
  );
};

export const CardSkeleton: React.FC<{ count?: number; className?: string }> = ({
  count = 1,
  className = '',
}) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="glass-panel p-5 rounded-2xl space-y-3 skeleton-shimmer"
        >
          <div className="h-4 bg-slate-700/50 rounded w-1/3" />
          <div className="h-3 bg-slate-700/30 rounded w-2/3" />
          <div className="h-3 bg-slate-700/20 rounded w-1/2" />
        </div>
      ))}
    </div>
  );
};