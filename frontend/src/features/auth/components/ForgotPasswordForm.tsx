import { useRef, useState } from 'react';
import type { ChangeEvent, FC, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Alert, Button, Card, FormField, Input } from '../../../components/common';
import { authApi } from '../api/authApi';
import { getAuthError } from '../utils/getAuthError';

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const ForgotPasswordForm: FC = () => {
  const navigate = useNavigate();
  const emailRef = useRef<HTMLInputElement>(null);
  const [email, setEmail] = useState(() => sessionStorage.getItem('password_reset_email') ?? '');
  const [error, setError] = useState('');
  const [requestError, setRequestError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    setEmail(event.target.value);
    setError('');
    setRequestError('');
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSubmitting) return;
    const normalizedEmail = email.trim().toLowerCase();
    if (!normalizedEmail || !EMAIL_PATTERN.test(normalizedEmail)) {
      setError(normalizedEmail ? 'Please enter a valid email address' : 'Email is required');
      emailRef.current?.focus();
      return;
    }

    setIsSubmitting(true);
    setRequestError('');
    try {
      await authApi.forgotPassword(normalizedEmail);
      sessionStorage.setItem('password_reset_email', normalizedEmail);
      sessionStorage.setItem(`password_reset_expiration_${normalizedEmail}`, String(Date.now() + 60000));
      navigate('/reset-password', { state: { email: normalizedEmail, requested: true } });
    } catch (err) {
      setRequestError(getAuthError(err, 'Unable to send a reset code. Please try again.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="mx-auto w-full max-w-md rounded-none border border-border-default p-6 shadow-elevated sm:p-10">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-serif italic text-text-primary">Reset access</h1>
        <p className="mt-4 text-sm tracking-wide text-text-secondary">Enter your email and we’ll send a six-digit recovery code.</p>
      </div>
      <form className="space-y-6" onSubmit={handleSubmit} noValidate>
        <FormField label="Email address" id="forgot-email" error={error} required>
          <Input ref={emailRef} id="forgot-email" name="email" type="email" autoComplete="email" value={email} onChange={handleChange} error={error} placeholder="you@example.com" />
        </FormField>
        {requestError && <Alert variant="error" message={requestError} />}
        <Button type="submit" size="lg" fullWidth isLoading={isSubmitting}>Send recovery code</Button>
      </form>
      <div className="mt-8 text-center text-sm text-text-secondary">
        <Link to="/login" className="font-semibold text-text-primary underline underline-offset-4 hover:opacity-80">Back to sign in</Link>
      </div>
    </Card>
  );
};

export default ForgotPasswordForm;
