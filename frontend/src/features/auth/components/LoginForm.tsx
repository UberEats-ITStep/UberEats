import { useState } from 'react';
import type { FC, FormEvent, ChangeEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import { getAuthError } from '../utils/getAuthError';
import { triggerMonochromeConfetti } from '../../../utils/confetti';
import { Card, FormField, Input, Button, Alert } from '../../../components/common';

const LoginForm: FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [requestError, setRequestError] = useState('');
  const [unverifiedEmail, setUnverifiedEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    const newErrors: { email?: string; password?: string } = {};
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setRequestError('');
    setUnverifiedEmail('');
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    setRequestError('');

    try {
      await login(formData);
      triggerMonochromeConfetti();
      navigate('/', { replace: true });
    } catch (error) {
      const errorMsg = getAuthError(error, 'Unable to sign in. Please try again.');
      // Detect unverified email errors from backend
      if (
        errorMsg.toLowerCase().includes('not been verified') || 
        errorMsg.toLowerCase().includes('email verification required') ||
        errorMsg.toLowerCase().includes('unverified')
      ) {
        setRequestError("Your account hasn't been verified yet.");
        setUnverifiedEmail(formData.email);
      } else {
        setRequestError(errorMsg);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto p-10 border border-border-default shadow-elevated rounded-none">
      <div className="text-center mb-10">
        <h2 className="text-4xl font-serif italic text-text-primary">Welcome back</h2>
        <p className="mt-4 text-sm text-text-secondary tracking-widest uppercase">Please enter your details</p>
      </div>

      <form className="space-y-6" onSubmit={handleLogin} noValidate>
        <div className="space-y-4">
          <FormField label="Email address" id="email" error={errors.email} required>
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              placeholder="you@example.com"
            />
          </FormField>

          <FormField label="Password" id="password" error={errors.password} required>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              placeholder="••••••••"
            />
          </FormField>
        </div>

        {requestError && (
          <Alert variant="error" message={requestError} className="my-4" />
        )}
        
        {unverifiedEmail && (
          <div className="pb-2">
            <Button
              type="button"
              variant="outline"
              fullWidth
              onClick={() => {
                sessionStorage.setItem('verification_email', unverifiedEmail);
                navigate('/verify-email', { state: { email: unverifiedEmail, autoResend: true } });
              }}
            >
              Verify Email
            </Button>
          </div>
        )}

        <div className="pt-2">
          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isSubmitting}
          >
            Sign in
          </Button>
        </div>
      </form>

      <div className="mt-8 text-center text-sm text-text-secondary">
        <span>Don't have an account? </span>
        <Link to="/register" className="font-semibold text-text-primary underline underline-offset-4 hover:opacity-80">
          Sign up
        </Link>
      </div>
    </Card>
  );
};

export default LoginForm;
