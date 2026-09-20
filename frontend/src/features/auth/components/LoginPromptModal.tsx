import { useEffect, useId, useRef } from 'react';
import type { FC, MouseEvent } from 'react';
import { createPortal } from 'react-dom';
import { useLocation, useNavigate } from 'react-router-dom';
import { Button } from '../../../components/common';

export interface LoginPromptModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  message?: string;
}

const LoginPromptModal: FC<LoginPromptModalProps> = ({
  isOpen,
  onClose,
  title = 'Log in to continue',
  message = 'You need an account to use this feature.',
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const dialogRef = useRef<HTMLDivElement>(null);
  const titleId = useId();
  const messageId = useId();

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const previouslyFocused = document.activeElement as HTMLElement | null;
    dialogRef.current?.querySelector<HTMLElement>('button')?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      previouslyFocused?.focus?.();
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  const goTo = (path: '/login' | '/register') => {
    onClose();
    navigate(path, { state: { from: location } });
  };
  const stopBubbling = (event: MouseEvent) => event.stopPropagation();

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 p-4"
      onClick={stopBubbling}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={messageId}
        className="w-full max-w-sm border border-border-default bg-background p-6 text-text-primary shadow-xl"
      >
        <h2 id={titleId} className="text-lg font-semibold">
          {title}
        </h2>
        <p id={messageId} className="mt-2 text-sm text-text-secondary">
          {message}
        </p>
        <div className="mt-6 flex flex-col gap-2 sm:flex-row">
          <Button type="button" variant="secondary" onClick={() => goTo('/login')}>
            Log in
          </Button>
          <Button type="button" variant="outline" onClick={() => goTo('/register')}>
            Create account
          </Button>
          <Button type="button" variant="outline" onClick={onClose}>
            Not now
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  );
};

export default LoginPromptModal;
