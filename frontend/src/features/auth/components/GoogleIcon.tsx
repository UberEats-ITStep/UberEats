import type { FC } from 'react';

interface GoogleIconProps {
  className?: string;
}

const GoogleIcon: FC<GoogleIconProps> = ({ className = 'h-5 w-5' }) => (
  <svg
    aria-hidden="true"
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M20 12a8 8 0 1 1-2.34-5.66"
      stroke="currentColor"
      strokeLinecap="square"
      strokeWidth="2.75"
    />
    <path
      d="M20 12h-7"
      stroke="currentColor"
      strokeLinecap="square"
      strokeWidth="2.75"
    />
  </svg>
);

export default GoogleIcon;
