import { isValidElement, cloneElement } from 'react';
import type { FC, ReactNode, ReactElement } from 'react';

export interface FormFieldProps {
  label: string;
  id: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  optionalLabel?: boolean;
  children: ReactNode;
  className?: string;
}

export const FormField: FC<FormFieldProps> = ({
  label,
  id,
  error,
  helperText,
  required = false,
  optionalLabel = false,
  children,
  className = '',
}) => {
  const errorId = `${id}-error`;
  const helperId = `${id}-helper`;

  // Clone children to automatically inject aria-describedby and id if needed
  const enhancedChildren = isValidElement(children)
    ? cloneElement(children as ReactElement<{ id?: string; 'aria-describedby'?: string; error?: boolean | string }>, {
        id: (children.props as { id?: string }).id || id,
        'aria-describedby': error
          ? errorId
          : helperText
          ? helperId
          : undefined,
        error: error ? true : (children.props as { error?: boolean | string }).error,
      })
    : children;

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-baseline justify-between">
        <label htmlFor={id} className="text-label">
          {label}
          {required && <span className="ml-1 text-status-error" aria-hidden="true">*</span>}
        </label>
        {optionalLabel && !required && (
          <span className="text-xs font-normal text-text-muted">(optional)</span>
        )}
      </div>

      <div className="mt-1">{enhancedChildren}</div>

      {error && (
        <p id={errorId} className="text-xs font-medium text-status-error" role="alert">
          {error}
        </p>
      )}

      {!error && helperText && (
        <p id={helperId} className="text-xs text-text-muted">
          {helperText}
        </p>
      )}
    </div>
  );
};

export default FormField;
