import type { FC } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../../../components/common';

export interface LoginPromptPanelProps {
  title?: string;
  message?: string;
  /** Called right before navigating away, e.g. to close a drawer. */
  onNavigate?: () => void;
  className?: string;
}

const LoginPromptPanel: FC<LoginPromptPanelProps> = ({
  title = 'Log in to continue',
  message = 'You need an account to use this feature.',
  onNavigate,
  className = '',
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  const goTo = (path: '/login' | '/register') => {
    onNavigate?.();
    navigate(path, { state: { from: location } });
  };

  return (
    <div className={`flex flex-col items-center justify-center gap-2 py-12 text-center ${className}`}>
      <h3 className="text-lg font-semibold text-text-primary">{title}</h3>
      <p className="max-w-sm text-sm text-text-secondary">{message}</p>
      <div className="mt-4 flex flex-wrap justify-center gap-3">
        <Button type="button" variant="accent" onClick={() => goTo('/login')}>
          Log in
        </Button>
        <Button type="button" variant="outline" onClick={() => goTo('/register')}>
          Create account
        </Button>
      </div>
    </div>
  );
};

export default LoginPromptPanel;