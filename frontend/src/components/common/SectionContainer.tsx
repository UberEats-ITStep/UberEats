import type { FC, HTMLAttributes, ReactNode } from 'react';

export interface SectionContainerProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  as?: 'section' | 'div' | 'main' | 'article' | 'header' | 'footer';
  width?: 'page' | 'content' | 'auth' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
}

const widthClasses = {
  page: 'container-page',
  content: 'container-content px-4 sm:px-6',
  auth: 'container-auth px-4 sm:px-6',
  full: 'w-full px-4 sm:px-6 lg:px-8',
};

const paddingClasses = {
  none: 'py-0',
  sm: 'py-6 sm:py-8',
  md: 'py-8 sm:py-12',
  lg: 'py-12 sm:py-16',
};

export const SectionContainer: FC<SectionContainerProps> = ({
  children,
  as: Component = 'section',
  width = 'page',
  padding = 'md',
  className = '',
  ...props
}) => {
  return (
    <Component
      className={`${widthClasses[width]} ${paddingClasses[padding]} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
};

export default SectionContainer;
