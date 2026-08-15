import { useEffect, type FC, type ReactNode } from 'react';

export interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export const Drawer: FC<DrawerProps> = ({ isOpen, onClose, title, children, footer }) => {
  // Prevent body scroll when drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-primary/70 transition-opacity backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Drawer Panel */}
      <div className="absolute inset-y-0 right-0 flex max-w-full">
        <div className="w-screen max-w-md animate-slide-in-right">
          <div className="flex h-full flex-col bg-surface shadow-elevated">
            
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border-default px-4 py-4 sm:px-6">
              <h2 className="text-lg font-bold text-text-primary">{title}</h2>
              <button
                type="button"
                className="rounded-sm text-text-muted hover:text-text-primary focus:outline-none focus:ring-2 focus:ring-accent"
                onClick={onClose}
              >
                <span className="sr-only">Close panel</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Content Body */}
            <div className="relative flex-1 px-4 py-6 sm:px-6 overflow-y-auto">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="border-t border-border-default px-4 py-4 sm:px-6 bg-secondary">
                {footer}
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default Drawer;
