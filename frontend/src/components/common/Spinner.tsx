import type { FC } from 'react';

export type SpinnerSize = 'sm' | 'md' | 'lg' | 'xl';
export type SpinnerColor = 'primary' | 'accent' | 'inverse' | 'muted';

export interface SpinnerProps {
  size?: SpinnerSize;
  color?: SpinnerColor;
  className?: string;
  label?: string;
}

const sizeClasses: Record<SpinnerSize, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-6 w-6 border-2',
  lg: 'h-8 w-8 border-3',
  xl: 'h-12 w-12 border-4',
};

const colorClasses: Record<SpinnerColor, string> = {
  primary: 'border-border-default border-t-primary',
  accent: 'border-border-default border-t-accent',
  inverse: 'border-white/30 border-t-white',
  muted: 'border-border-default border-t-text-muted',
};

export const Spinner: FC<SpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = '',
  label = 'Loading...',
}) => {
  return (
    <div
      role="status"
      aria-label={label}
      className={`inline-block animate-spin rounded-full ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
    >
      <span className="sr-only">{label}</span>
    </div>
  );
};

export default Spinner;
