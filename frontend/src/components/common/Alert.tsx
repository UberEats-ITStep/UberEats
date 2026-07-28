import type { FC, ReactNode } from 'react';
import Button from './Button';

export type AlertVariant = 'error' | 'warning' | 'info' | 'success';

export interface AlertProps {
  title?: string;
  message: string;
  variant?: AlertVariant;
  onRetry?: () => void;
  retryLabel?: string;
  action?: ReactNode;
  className?: string;
}

const variantClasses: Record<AlertVariant, string> = {
  error: 'bg-status-error-muted border-red-200 text-red-900',
  warning: 'bg-status-warning-muted border-amber-200 text-amber-900',
  info: 'bg-status-info-muted border-blue-200 text-blue-900',
  success: 'bg-status-success-muted border-emerald-200 text-emerald-900',
};

const buttonVariants: Record<AlertVariant, 'danger' | 'primary' | 'secondary'> = {
  error: 'danger',
  warning: 'primary',
  info: 'primary',
  success: 'primary',
};

export const Alert: FC<AlertProps> = ({
  title,
  message,
  variant = 'error',
  onRetry,
  retryLabel = 'Try again',
  action,
  className = '',
}) => {
  return (
    <div
      role="alert"
      className={`rounded-lg border p-6 text-center ${variantClasses[variant]} ${className}`}
    >
      {title && <h4 className="mb-1 text-base font-bold">{title}</h4>}
      <p className="text-sm leading-relaxed">{message}</p>
      
      {(onRetry || action) && (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3">
          {onRetry && (
            <Button
              variant={buttonVariants[variant]}
              size="sm"
              onClick={onRetry}
            >
              {retryLabel}
            </Button>
          )}
          {action}
        </div>
      )}
    </div>
  );
};

export default Alert;
