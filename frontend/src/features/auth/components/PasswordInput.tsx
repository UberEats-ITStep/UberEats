import { forwardRef, useState } from 'react';
import { Input } from '../../../components/common';
import type { InputProps } from '../../../components/common';

export const PasswordInput = forwardRef<HTMLInputElement, InputProps>((props, ref) => {
  const [visible, setVisible] = useState(false);

  return (
    <Input
      ref={ref}
      {...props}
      type={visible ? 'text' : 'password'}
      rightIcon={(
        <button
          type="button"
          onClick={() => setVisible((value) => !value)}
          className="rounded-sm p-1 text-text-muted transition-opacity hover:text-text-primary focus:outline-none focus:ring-1 focus:ring-primary"
          aria-label={visible ? 'Hide password' : 'Show password'}
          aria-pressed={visible}
        >
          {visible ? (
            <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="square" strokeWidth={1.8} d="M3 3l18 18M10.6 10.7a2 2 0 002.7 2.7M9.9 4.3A10.8 10.8 0 0112 4c5.5 0 9 6 9 6a16 16 0 01-2.2 3M6.6 6.6C4.3 8.2 3 10 3 10s3.5 6 9 6a9.8 9.8 0 004-.8" />
            </svg>
          ) : (
            <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="square" strokeWidth={1.8} d="M3 12s3.5-6 9-6 9 6 9 6-3.5 6-9 6-9-6-9-6z" />
              <circle cx="12" cy="12" r="2.5" strokeWidth={1.8} />
            </svg>
          )}
        </button>
      )}
    />
  );
});

PasswordInput.displayName = 'PasswordInput';

export default PasswordInput;
