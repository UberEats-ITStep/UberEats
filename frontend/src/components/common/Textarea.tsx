import { forwardRef } from 'react';
import type { TextareaHTMLAttributes } from 'react';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean | string;
  fullWidth?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ error, fullWidth = true, className = '', id, ...props }, ref) => {
    const baseClasses =
      'block py-2.5 px-3.5 text-sm rounded-none transition-base bg-surface placeholder:text-text-muted text-text-primary focus:outline-none focus:ring-1 focus:ring-primary focus:ring-offset-1 disabled:cursor-not-allowed disabled:bg-secondary disabled:opacity-70';

    const borderClass = error
      ? 'border border-status-error focus:ring-status-error focus:border-status-error text-status-error'
      : 'border border-border-default focus:ring-primary focus:border-primary';

    const widthClass = fullWidth ? 'w-full' : '';

    return (
      <textarea
        id={id}
        ref={ref}
        aria-invalid={Boolean(error)}
        className={`${baseClasses} ${borderClass} ${widthClass} ${className}`}
        {...props}
      />
    );
  },
);

Textarea.displayName = 'Textarea';

export default Textarea;
