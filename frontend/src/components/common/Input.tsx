import { forwardRef } from 'react';
import type { InputHTMLAttributes, ReactNode } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean | string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      error,
      leftIcon,
      rightIcon,
      fullWidth = true,
      className = '',
      disabled,
      id,
      ...props
    },
    ref,
  ) => {
    const baseInputClasses =
      'appearance-none block py-2.5 px-3.5 text-sm rounded-none transition-base bg-surface placeholder:text-text-muted text-text-primary focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-1 disabled:cursor-not-allowed disabled:bg-secondary disabled:opacity-70';

    const borderClass = error
      ? 'border border-status-error focus:ring-status-error focus:border-status-error text-status-error'
      : 'border border-border-default focus:ring-primary focus:border-primary';

    const widthClass = fullWidth ? 'w-full' : '';
    const paddingLeftClass = leftIcon ? 'pl-10' : '';
    const paddingRightClass = rightIcon ? 'pr-10' : '';

    return (
      <div className={`relative inline-flex items-center ${widthClass}`}>
        {leftIcon && (
          <div className="pointer-events-none absolute left-3 flex items-center text-text-muted">
            {leftIcon}
          </div>
        )}
        <input
          ref={ref}
          id={id}
          disabled={disabled}
          aria-invalid={Boolean(error)}
          className={`${baseInputClasses} ${borderClass} ${paddingLeftClass} ${paddingRightClass} ${widthClass} ${className}`}
          {...props}
        />
        {rightIcon && (
          <div className="absolute right-3 flex items-center text-text-muted">
            {rightIcon}
          </div>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';

export default Input;
