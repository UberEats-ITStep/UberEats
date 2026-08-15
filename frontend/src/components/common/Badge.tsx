import type { FC, ReactNode } from 'react';

export type BadgeVariant =
  | 'brand'
  | 'primary'
  | 'secondary'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'neutral';

export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  icon?: ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  brand: 'bg-primary text-text-inverse font-bold',
  primary: 'bg-primary text-text-inverse font-semibold',
  secondary: 'bg-secondary text-text-secondary font-medium border border-border-default',
  neutral: 'bg-surface-muted text-text-primary font-medium border border-border-default',
  success: 'bg-surface text-text-primary font-semibold border border-status-success',
  warning: 'bg-surface text-text-primary font-semibold border border-status-warning',
  error: 'bg-surface text-text-primary font-semibold border border-status-error',
  info: 'bg-surface text-text-primary font-semibold border border-border-default',
};

const sizeClasses: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs gap-1',
  md: 'px-2.5 py-1 text-xs sm:text-sm gap-1.5',
  lg: 'px-3.5 py-1.5 text-sm gap-2',
};

export const Badge: FC<BadgeProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  icon,
  className = '',
}) => {
  return (
    <span
      className={`inline-flex items-center justify-center shrink-0 rounded-none leading-none transition-base ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {icon && <span className="shrink-0 inline-flex">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};

export default Badge;
