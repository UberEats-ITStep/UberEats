import { useState, useRef, useEffect } from 'react';
import type { FC } from 'react';

export interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  'aria-label'?: string;
  className?: string;
}

export const Select: FC<SelectProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Select an option',
  'aria-label': ariaLabel,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((opt) => opt.value === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
  };

  return (
    <div className={`relative inline-block text-left ${className}`} ref={containerRef}>
      <button
        type="button"
        className={`flex items-center justify-between gap-2 rounded-none border border-border-default bg-surface px-4 py-1.5 text-sm font-medium text-text-secondary transition-base hover:border-primary hover:text-text-primary focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary ${
          isOpen ? 'border-primary text-text-primary ring-1 ring-primary' : ''
        }`}
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={ariaLabel}
      >
        <span className="truncate">{selectedOption ? selectedOption.label : placeholder}</span>
        <svg
          className={`h-4 w-4 shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180 text-primary' : 'text-text-muted'}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-50 mt-1 w-max min-w-[140px] origin-top-right rounded-none border border-border-default bg-surface shadow-elevated animate-fade-in overflow-hidden">
          <ul
            className="max-h-60 overflow-auto focus:outline-none"
            role="listbox"
            aria-activedescendant={selectedOption ? `option-${selectedOption.value}` : undefined}
          >
            {options.map((option) => (
              <li
                key={option.value}
                id={`option-${option.value}`}
                role="option"
                aria-selected={value === option.value}
                className={`relative cursor-pointer select-none py-2 px-4 text-sm transition-base hover:bg-secondary hover:text-text-primary ${
                  value === option.value ? 'bg-secondary text-primary font-bold' : 'text-text-primary'
                }`}
                onClick={() => handleSelect(option.value)}
              >
                {option.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Select;
