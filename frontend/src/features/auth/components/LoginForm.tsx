import { useState } from 'react';
import type { FC, FormEvent, ChangeEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import { getAuthError } from '../utils/getAuthError';
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
      navigate('/', { replace: true });
    } catch (error) {
      setRequestError(getAuthError(error, 'Unable to sign in. Please try again.'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card elevation="elevated" padding="lg" className="w-full max-w-md space-y-6">
      <div className="text-center">
        <h2 className="text-page-title">Welcome back</h2>
        <p className="mt-2 text-body">Please enter your details to sign in.</p>
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleLogin} noValidate>
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

        <div>
          <Button
            type="submit"
            variant="primary"
            size="md"
            fullWidth
            isLoading={isSubmitting}
          >
            Sign in
          </Button>
        </div>
      </form>

      <div className="text-center text-sm text-text-secondary">
        <span>Don't have an account? </span>
        <Link to="/register" className="font-semibold text-primary transition-base hover:text-accent">
          Sign up
        </Link>
      </div>
    </Card>
  );
};

export default LoginForm;
