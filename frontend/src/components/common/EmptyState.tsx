import type { FC, ReactNode } from 'react';

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}

export const EmptyState: FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center rounded-xl border border-border-default bg-surface p-12 text-center shadow-subtle ${className}`}
    >
      {icon ? (
        <div className="mb-6 text-text-primary">{icon}</div>
      ) : (
        <div className="mb-6 flex justify-center text-text-primary">
          <svg
            viewBox="0 0 64 64"
            className="h-14 w-14"
            aria-hidden="true"
          >
            {/* Bag body */}
            <rect x="16" y="26" width="32" height="34" className="stroke-text-primary" strokeWidth="1.5" fill="none" />
            
            {/* Bag handles */}
            <path d="M26 26 C 26 12, 38 12, 38 26" className="stroke-text-primary" strokeWidth="1.5" fill="none" />
          </svg>
        </div>
      )}
      <h3 className="text-section-title">{title}</h3>
      {description && (
        <p className="mt-2 max-w-md text-body">{description}</p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
};

export default EmptyState;
