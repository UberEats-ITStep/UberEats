import type { FC, ReactNode } from 'react';
import Spinner from './Spinner';

export interface LoadingStateProps {
  message?: string;
  fullScreen?: boolean;
  minHeight?: string;
  className?: string;
  children?: ReactNode;
}

export const LoadingState: FC<LoadingStateProps> = ({
  message = 'Loading...',
  fullScreen = false,
  minHeight = 'min-h-[50vh]',
  className = '',
  children,
}) => {
  const containerHeight = fullScreen ? 'min-h-screen' : minHeight;

  return (
    <div
      role="status"
      className={`flex flex-col items-center justify-center p-8 text-center text-text-secondary ${containerHeight} ${className}`}
    >
      <Spinner size="lg" color="primary" className="mb-4" />
      {children ? (
        <div className="mt-2">{children}</div>
      ) : (
        <p className="text-body font-medium">{message}</p>
      )}
    </div>
  );
};

export default LoadingState;
