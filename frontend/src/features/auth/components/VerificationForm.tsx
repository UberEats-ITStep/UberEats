import { useState, useEffect } from 'react';
import type { FC } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import { authApi } from '../api/authApi';
import { getAuthError } from '../utils/getAuthError';
import { triggerMonochromeConfetti } from '../../../utils/confetti';
import { Card, Button, Alert } from '../../../components/common';
import OtpInput from './OtpInput';

export const VerificationForm: FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithTokens } = useAuth();
  
  const [email] = useState<string>(() => {
    const routerEmail = location.state?.email as string | undefined;
    const sessionEmail = sessionStorage.getItem('verification_email');
    if (routerEmail) {
      sessionStorage.setItem('verification_email', routerEmail);
      return routerEmail;
    }
    return sessionEmail || '';
  });
  
  const [code, setCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isVerified, setIsVerified] = useState(false);
  
  const [cooldown, setCooldown] = useState(() => {
    const storedExpiration = sessionStorage.getItem(`resend_expiration_${email}`);
    if (storedExpiration) {
      const remaining = Math.floor((parseInt(storedExpiration, 10) - Date.now()) / 1000);
      if (remaining > 0) {
        return remaining;
      } else {
        sessionStorage.removeItem(`resend_expiration_${email}`);
      }
    }
    
    // Automatically start cooldown if navigating from Registration
    if (location.state?.startCooldown) {
      const expireTime = Date.now() + 60000;
      sessionStorage.setItem(`resend_expiration_${email}`, expireTime.toString());
      return 60;
    }
    return 0;
  });

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  // Cooldown interval
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = window.setInterval(() => {
      setCooldown((prev) => {
        if (prev <= 1) {
          sessionStorage.removeItem(`resend_expiration_${email}`);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [cooldown, email]);

  const handleVerify = async (submissionCode: string) => {
    if (submissionCode.length !== 6 || isVerifying || isVerified) return;
    
    setIsVerifying(true);
    setError('');
    setSuccess('');

    try {
      const { access, refresh } = await authApi.verifyEmail(email, submissionCode);
      setIsVerified(true);
      sessionStorage.removeItem('verification_email');
      triggerMonochromeConfetti();
      
      // Auto-redirect to home after delay to allow animation
      setTimeout(() => {
        void loginWithTokens(access, refresh).then(() => {
          navigate('/', { replace: true });
        });
      }, 2000);
    } catch (err) {
      setError(getAuthError(err, 'Verification failed. Please try again.'));
      setIsVerifying(false);
      // Auto-focus first input on error
      document.querySelector<HTMLInputElement>('[aria-label="Verification code digit 1"]')?.focus();
    }
  };

  const handleResend = async () => {
    if (isResending || cooldown > 0) return;
    setIsResending(true);
    setError('');
    setSuccess('');

    try {
      await authApi.resendVerification(email);
      setSuccess(`A new verification code has been sent to ${email}`);
      const expireTime = Date.now() + 60000;
      sessionStorage.setItem(`resend_expiration_${email}`, expireTime.toString());
      setCooldown(60);
    } catch (err) {
      const errorMsg = getAuthError(err, 'Failed to resend code.');
      // If backend returns a throttle message, extract seconds and start timer
      const match = errorMsg.match(/available in (\d+) seconds/i) || errorMsg.match(/wait (\d+) seconds/i);
      if (match) {
        const seconds = parseInt(match[1], 10);
        const expireTime = Date.now() + (seconds * 1000);
        sessionStorage.setItem(`resend_expiration_${email}`, expireTime.toString());
        setCooldown(seconds);
      } else {
        setError(errorMsg);
      }
    } finally {
      setIsResending(false);
    }
  };

  useEffect(() => {
    if (location.state?.autoResend && email) {
      // Clear autoResend to prevent double-firing
      navigate(location.pathname, { replace: true, state: { ...location.state, autoResend: false } });
      const autoResendKey = `verification_auto_resend_${email}`;
      const lastAutoResend = Number(sessionStorage.getItem(autoResendKey) ?? 0);
      const wasJustRequested = Date.now() - lastAutoResend < 5000;

      if (cooldown === 0 && !isResending && !wasJustRequested) {
        // Persisted synchronously so React StrictMode remounts cannot issue a
        // second request before the first response starts the normal cooldown.
        sessionStorage.setItem(autoResendKey, Date.now().toString());
        // eslint-disable-next-line react-hooks/set-state-in-effect
        void handleResend();
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state?.autoResend, email]);

  if (!email && !location.state?.email && !sessionStorage.getItem('verification_email')) {
    return (
      <Card className="w-full max-w-md mx-auto p-10 border border-border-default shadow-elevated rounded-none text-center">
        <h2 className="text-4xl font-serif italic text-text-primary mb-4">Session Expired</h2>
        <p className="text-sm tracking-widest uppercase text-text-secondary mb-8">
          Unable to determine email.
        </p>
        <div className="flex gap-4">
          <Button variant="outline" fullWidth onClick={() => navigate('/register', { replace: true })}>
            Register
          </Button>
          <Button variant="primary" fullWidth onClick={() => navigate('/login', { replace: true })}>
            Login
          </Button>
        </div>
      </Card>
    );
  }

  if (isVerified) {
    return (
      <Card className="w-full max-w-md mx-auto p-12 border border-border-default shadow-elevated rounded-none text-center">
        <div className="flex flex-col items-center justify-center space-y-6">
          <div className="relative flex h-20 w-20 items-center justify-center rounded-none bg-text-primary text-surface overflow-hidden transition-all duration-1000 ease-[cubic-bezier(0.2,0.8,0.2,1)] scale-100 animate-in fade-in zoom-in-50 spin-in-180">
            <svg className="h-10 w-10 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="square" strokeLinejoin="miter" strokeWidth={2} d="M5 13l4 4L19 7" className="animate-[dash_1s_ease-out_forwards]" strokeDasharray="24" strokeDashoffset="24" />
            </svg>
          </div>
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300 fill-mode-both">
            <h2 className="text-4xl font-serif italic text-text-primary mb-2">Verified.</h2>
            <p className="text-sm tracking-widest uppercase text-text-secondary">
              Welcome to BiteUp
            </p>
          </div>
        </div>
        <style>{`
          @keyframes dash {
            to { stroke-dashoffset: 0; }
          }
        `}</style>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto p-10 border border-border-default shadow-elevated rounded-none">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-serif italic text-text-primary mb-4">Verify Identity</h2>
        <p className="text-sm font-medium tracking-wide text-text-secondary">
          Code sent to <span className="text-text-primary font-bold">{email}</span>
        </p>
      </div>

      <div className="space-y-8">
        <OtpInput
          value={code}
          onChange={(value) => { setCode(value); setError(''); }}
          onComplete={(value) => window.setTimeout(() => void handleVerify(value), 300)}
          disabled={isVerifying || isVerified}
          error={Boolean(error)}
          autoFocus
        />

        {error && <Alert variant="error" message={error} />}
        {success && !isVerified && <Alert variant="success" message={success} />}

        <div className="pt-2">
          <Button
            type="button"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isVerifying}
            disabled={code.length !== 6 || isVerified}
            onClick={() => void handleVerify(code)}
          >
            Verify
          </Button>
        </div>

        <div className="text-center text-sm text-text-secondary pt-4 border-t border-border-default">
          <button
            type="button"
            onClick={handleResend}
            disabled={cooldown > 0 || isResending}
            className="font-medium tracking-widest uppercase text-text-primary hover:opacity-80 transition-opacity disabled:opacity-50 disabled:hover:opacity-50"
          >
            {isResending 
              ? 'Sending...' 
              : cooldown > 0 
                ? `Resend in ${formatTime(cooldown)}` 
                : 'Resend Code'}
          </button>
        </div>
      </div>
    </Card>
  );
};

export default VerificationForm;
