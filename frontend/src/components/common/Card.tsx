import type { FC, HTMLAttributes, ReactNode } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  interactive?: boolean;
  elevation?: 'none' | 'subtle' | 'elevated' | 'floating';
  radius?: 'md' | 'lg' | 'xl';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
}

const elevationClasses = {
  none: 'shadow-none',
  subtle: 'shadow-subtle border border-border-subtle/50',
  elevated: 'shadow-elevated',
  floating: 'shadow-floating',
};

const radiusClasses = {
  md: 'rounded-none',
  lg: 'rounded-none',
  xl: 'rounded-none',
};

const paddingClasses = {
  none: 'p-0',
  sm: 'p-3 sm:p-4',
  md: 'p-5 sm:p-6',
  lg: 'p-6 sm:p-8',
};

export const Card: FC<CardProps> = ({
  children,
  interactive = false,
  elevation = 'subtle',
  radius = 'lg',
  padding = 'md',
  className = '',
  ...props
}) => {
  const interactiveClasses = interactive
    ? 'transition-card hover:shadow-elevated hover:border-border-focus focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2 cursor-pointer'
    : '';

  return (
    <div
      className={`bg-card text-text-primary overflow-hidden ${elevationClasses[elevation]} ${radiusClasses[radius]} ${paddingClasses[padding]} ${interactiveClasses} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
