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
        <div className="mb-4 text-4xl text-text-muted">{icon}</div>
      ) : (
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary text-2xl text-text-muted">
          🍽️
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
