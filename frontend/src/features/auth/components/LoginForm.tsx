import { useState } from 'react';
import type { FC, FormEvent, ChangeEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../hooks/useAuth';
import { getAuthError } from '../utils/getAuthError';

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
    <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <div className="text-center">
        <h2 className="text-3xl font-extrabold text-gray-900">Welcome back</h2>
        <p className="mt-2 text-sm text-gray-600">Please enter your details to sign in.</p>
      </div>

      <form className="mt-8 space-y-6" onSubmit={handleLogin} noValidate>
        <div className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email address
            </label>
            <div className="mt-1">
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleChange}
                className={`appearance-none block w-full px-3 py-2 border ${
                  errors.email ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-green-500 focus:border-green-500'
                } rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm`}
                placeholder="you@example.com"
              />
              {errors.email && <p className="mt-2 text-sm text-red-600" id="email-error">{errors.email}</p>}
            </div>
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <div className="mt-1">
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={formData.password}
                onChange={handleChange}
                className={`appearance-none block w-full px-3 py-2 border ${
                  errors.password ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300 focus:ring-green-500 focus:border-green-500'
                } rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm`}
                placeholder="••••••••"
              />
              {errors.password && <p className="mt-2 text-sm text-red-600" id="password-error">{errors.password}</p>}
            </div>
          </div>
        </div>

        <div>
          {requestError && (
            <p className="mb-4 text-sm text-center text-red-600" role="alert">
              {requestError}
            </p>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </div>
      </form>

      <div className="text-center text-sm">
        <span className="text-gray-600">Don't have an account? </span>
        <Link to="/register" className="font-medium text-green-600 hover:text-green-500 transition-colors">
          Sign up
        </Link>
      </div>
    </div>
  );
};

export default LoginForm;
