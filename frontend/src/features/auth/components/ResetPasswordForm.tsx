import axios from 'axios';
import { useEffect, useRef, useState } from 'react';
import type { ChangeEvent, FC, FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Alert, Button, Card, FormField, Input } from '../../../components/common';
import { authApi } from '../api/authApi';
import { getAuthError } from '../utils/getAuthError';
import OtpInput from './OtpInput';
import PasswordInput from './PasswordInput';

type Field = 'email' | 'verification_code' | 'new_password' | 'confirm_password';
type Errors = Partial<Record<Field, string>>;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const getFieldErrors = (error: unknown): Errors => {
  if (!axios.isAxiosError<Record<string, string | string[]>>(error) || !error.response?.data) return {};
  const result: Errors = {};
  for (const field of ['email', 'verification_code', 'new_password', 'confirm_password'] as Field[]) {
    const value = error.response.data[field];
    if (value) result[field] = Array.isArray(value) ? value.join(' ') : value;
  }
  return result;
};

const ResetPasswordForm: FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const emailRef = useRef<HTMLInputElement>(null);
  const newPasswordRef = useRef<HTMLInputElement>(null);
  const confirmPasswordRef = useRef<HTMLInputElement>(null);
  const initialEmail = (location.state?.email as string | undefined) ?? sessionStorage.getItem('password_reset_email') ?? '';
  const [form, setForm] = useState({ email: initialEmail, verification_code: '', new_password: '', confirm_password: '' });
  const [errors, setErrors] = useState<Errors>({});
  const [requestError, setRequestError] = useState('');
  const [success, setSuccess] = useState('');
  const [resendSuccess, setResendSuccess] = useState(() => initialEmail
    ? 'If an account exists, a recovery code has been sent.'
    : '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(() => {
    const expiry = initialEmail ? Number(sessionStorage.getItem(`password_reset_expiration_${initialEmail}`)) : 0;
    return Math.max(0, Math.ceil((expiry - Date.now()) / 1000));
  });

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = window.setInterval(() => setCooldown((value) => Math.max(0, value - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [cooldown]);

  const update = (field: Field, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
    setRequestError('');
    setResendSuccess('');
  };

  const validate = (): Errors => {
    const next: Errors = {};
    if (!form.email.trim()) next.email = 'Email is required';
    else if (!EMAIL_PATTERN.test(form.email.trim())) next.email = 'Please enter a valid email address';
    if (form.verification_code.length !== 6) next.verification_code = 'Enter the six-digit verification code';
    if (!form.new_password) next.new_password = 'New password is required';
    if (!form.confirm_password) next.confirm_password = 'Please confirm your new password';
    else if (form.new_password !== form.confirm_password) next.confirm_password = 'Passwords do not match';
    return next;
  };

  const focusFirstError = (next: Errors) => {
    if (next.email) emailRef.current?.focus();
    else if (next.verification_code) document.querySelector<HTMLInputElement>('[aria-label="Verification code digit 1"]')?.focus();
    else if (next.new_password) newPasswordRef.current?.focus();
    else confirmPasswordRef.current?.focus();
  };

  const handleSubmit = async (event?: FormEvent) => {
    event?.preventDefault();
    if (isSubmitting || success) return;
    const nextErrors = validate();
    if (Object.keys(nextErrors).length) {
      setErrors(nextErrors);
      focusFirstError(nextErrors);
      return;
    }
    setIsSubmitting(true);
    setRequestError('');
    try {
      const response = await authApi.resetPassword({ ...form, email: form.email.trim().toLowerCase() });
      setSuccess(response.detail || 'Password reset successful. Redirecting to sign in…');
      sessionStorage.removeItem('password_reset_email');
      sessionStorage.removeItem(`password_reset_expiration_${form.email.trim().toLowerCase()}`);
      window.setTimeout(() => navigate('/login', { replace: true }), 2000);
    } catch (err) {
      const fieldErrors = getFieldErrors(err);
      setErrors(fieldErrors);
      if (Object.keys(fieldErrors).length) focusFirstError(fieldErrors);
      else setRequestError(getAuthError(err, 'Unable to reset your password. Please try again.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const resend = async () => {
    const email = form.email.trim().toLowerCase();
    if (isResending || cooldown > 0 || !EMAIL_PATTERN.test(email)) {
      if (!EMAIL_PATTERN.test(email)) { setErrors({ email: 'Enter a valid email before requesting a code' }); emailRef.current?.focus(); }
      return;
    }
    setIsResending(true);
    setRequestError('');
    try {
      await authApi.forgotPassword(email);
      sessionStorage.setItem('password_reset_email', email);
      sessionStorage.setItem(`password_reset_expiration_${email}`, String(Date.now() + 60000));
      setCooldown(60);
      setResendSuccess('If an account exists, a new recovery code has been sent.');
      window.setTimeout(() => setResendSuccess(''), 4000);
    } catch (err) {
      setRequestError(getAuthError(err, 'Unable to resend the recovery code.'));
    } finally { setIsResending(false); }
  };

  const minutes = `${Math.floor(cooldown / 60)}:${String(cooldown % 60).padStart(2, '0')}`;

  return (
    <Card className="mx-auto w-full max-w-md rounded-none border border-border-default p-6 shadow-elevated sm:p-10">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-serif italic text-text-primary">Choose a password</h1>
        <p className="mt-4 text-sm tracking-wide text-text-secondary">Enter the code from your email and set a new password.</p>
      </div>
      <form className="space-y-5" onSubmit={(event) => void handleSubmit(event)} noValidate>
        <FormField label="Email address" id="reset-email" error={errors.email} required>
          <Input ref={emailRef} id="reset-email" type="email" autoComplete="email" value={form.email} onChange={(e: ChangeEvent<HTMLInputElement>) => update('email', e.target.value)} error={errors.email} />
        </FormField>
        <FormField label="Verification code" id="reset-code" error={errors.verification_code} required>
          <OtpInput value={form.verification_code} onChange={(value) => update('verification_code', value)} onComplete={() => newPasswordRef.current?.focus()} onEnter={() => void handleSubmit()} disabled={isSubmitting || Boolean(success)} error={Boolean(errors.verification_code)} />
        </FormField>
        <FormField label="New password" id="reset-new-password" error={errors.new_password} required>
          <PasswordInput ref={newPasswordRef} id="reset-new-password" autoComplete="new-password" value={form.new_password} onChange={(e) => update('new_password', e.target.value)} error={errors.new_password} disabled={Boolean(success)} />
        </FormField>
        <FormField label="Confirm password" id="reset-confirm-password" error={errors.confirm_password} required>
          <PasswordInput ref={confirmPasswordRef} id="reset-confirm-password" autoComplete="new-password" value={form.confirm_password} onChange={(e) => update('confirm_password', e.target.value)} error={errors.confirm_password} disabled={Boolean(success)} />
        </FormField>
        {requestError && <Alert variant="error" message={requestError} />}
        {resendSuccess && <Alert variant="success" message={resendSuccess} />}
        {success && <Alert variant="success" message={success} />}
        <Button type="submit" size="lg" fullWidth isLoading={isSubmitting} disabled={Boolean(success)}>Reset password</Button>
        <div className="text-center text-sm text-text-secondary">
          <button type="button" onClick={() => void resend()} disabled={cooldown > 0 || isResending} className="font-medium uppercase tracking-widest text-text-primary hover:opacity-80 disabled:opacity-50">
            {isResending ? 'Sending…' : cooldown > 0 ? `Resend in ${minutes}` : 'Resend code'}
          </button>
        </div>
      </form>
      <div className="mt-6 text-center text-sm"><Link to="/login" className="text-text-primary underline underline-offset-4">Back to sign in</Link></div>
    </Card>
  );
};

export default ResetPasswordForm;
