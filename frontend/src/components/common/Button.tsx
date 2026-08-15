import type { ButtonHTMLAttributes, FC, ReactNode } from 'react';

export type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'outline'
  | 'outline-inverse'
  | 'ghost'
  | 'ghost-inverse'
  | 'danger'
  | 'accent';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  children?: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-primary text-text-inverse hover:bg-primary-hover active:bg-primary-active shadow-subtle focus:ring-primary',
  secondary:
    'bg-secondary text-text-primary border border-transparent hover:border-border-default active:bg-muted focus:ring-primary',
  outline:
    'border border-border-default bg-surface text-text-primary hover:bg-secondary active:bg-muted focus:ring-primary',
  'outline-inverse':
    'border border-border-default bg-transparent text-white hover:bg-white/10 active:bg-white/20 focus:ring-white',
  ghost:
    'bg-transparent text-text-primary hover:bg-secondary active:bg-muted focus:ring-primary',
  'ghost-inverse':
    'bg-transparent text-slate-200 hover:bg-white/10 hover:text-white active:bg-white/20 focus:ring-white',
  danger:
    'bg-primary text-text-inverse hover:bg-primary-hover active:bg-primary-active shadow-subtle focus:ring-primary', // Muted danger
  accent:
    'bg-primary text-text-inverse hover:bg-primary-hover active:bg-primary-active shadow-subtle focus:ring-primary', // Muted accent
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'py-1.5 px-3 text-xs font-medium rounded-none gap-1.5',
  md: 'py-2.5 px-5 text-sm font-medium rounded-none gap-2',
  lg: 'py-3.5 px-6 text-base font-medium rounded-none gap-2.5',
};

export const Button: FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className = '',
  disabled,
  children,
  ...props
}) => {
  const baseClasses =
    'inline-flex items-center justify-center font-button transition-base hover:-translate-y-px focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-1 disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0';

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      type="button"
      disabled={disabled || isLoading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${className}`}
      {...props}
    >
      {isLoading ? (
        <>
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent inline-block" aria-hidden="true" />
          <span>{children ?? 'Loading...'}</span>
        </>
      ) : (
        <>
          {leftIcon && <span className="shrink-0 inline-flex">{leftIcon}</span>}
          {children && <span>{children}</span>}
          {rightIcon && <span className="shrink-0 inline-flex">{rightIcon}</span>}
        </>
      )}
    </button>
  );
};

export default Button;
