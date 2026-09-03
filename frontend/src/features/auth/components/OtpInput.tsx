import { useRef } from 'react';
import type { ChangeEvent, ClipboardEvent, FC, KeyboardEvent } from 'react';

interface OtpInputProps {
  value: string;
  onChange: (value: string) => void;
  onComplete?: (value: string) => void;
  onEnter?: (value: string) => void;
  disabled?: boolean;
  error?: boolean;
  autoFocus?: boolean;
}

export const OtpInput: FC<OtpInputProps> = ({ value, onChange, onComplete, onEnter, disabled, error, autoFocus }) => {
  const refs = useRef<(HTMLInputElement | null)[]>([]);
  const digits = Array.from({ length: 6 }, (_, index) => value[index] ?? '');

  const setDigit = (index: number, event: ChangeEvent<HTMLInputElement>) => {
    const entered = event.target.value.replace(/\D/g, '');
    if (!entered) return;
    const next = [...digits];
    const targetIndex = Math.min(index, value.length);
    next[targetIndex] = entered.at(-1) ?? '';
    const result = next.join('');
    onChange(result);
    if (targetIndex < 5) refs.current[targetIndex + 1]?.focus();
    else onComplete?.(result);
  };

  const handleKeyDown = (index: number, event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Backspace') {
      event.preventDefault();
      const next = [...digits];
      if (next[index]) next[index] = '';
      else if (index > 0) {
        next[index - 1] = '';
        refs.current[index - 1]?.focus();
      }
      onChange(next.join(''));
    } else if (event.key === 'ArrowLeft') refs.current[Math.max(0, index - 1)]?.focus();
    else if (event.key === 'ArrowRight') refs.current[Math.min(5, index + 1)]?.focus();
    else if (event.key === 'Enter' && value.length === 6) (onEnter ?? onComplete)?.(value);
  };

  const handlePaste = (event: ClipboardEvent<HTMLInputElement>) => {
    event.preventDefault();
    const pasted = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (!pasted) return;
    onChange(pasted);
    refs.current[Math.min(pasted.length, 6) - 1]?.focus();
    if (pasted.length === 6) onComplete?.(pasted);
  };

  return (
    <div className="flex justify-between gap-2 sm:gap-3" role="group" aria-label="Six-digit verification code">
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={(element) => { refs.current[index] = element; }}
          type="text"
          inputMode="numeric"
          autoComplete={index === 0 ? 'one-time-code' : 'off'}
          pattern="[0-9]*"
          maxLength={1}
          value={digit}
          onChange={(event) => setDigit(index, event)}
          onKeyDown={(event) => handleKeyDown(index, event)}
          onPaste={handlePaste}
          disabled={disabled}
          autoFocus={autoFocus && index === 0}
          aria-label={`Verification code digit ${index + 1}`}
          aria-invalid={error}
          className={`aspect-square w-full min-w-0 flex-1 rounded-none border bg-surface text-center text-xl font-serif text-text-primary shadow-subtle transition-base focus:outline-none disabled:opacity-50 sm:text-2xl ${error ? 'border-status-error focus:border-status-error' : 'border-border-default focus:border-text-primary'}`}
        />
      ))}
    </div>
  );
};

export default OtpInput;
