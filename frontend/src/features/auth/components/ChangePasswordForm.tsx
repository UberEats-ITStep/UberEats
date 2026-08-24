import axios from 'axios';
import { useRef, useState } from 'react';
import type { ChangeEvent, FC, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, Button, FormField } from '../../../components/common';
import { useAuth } from '../../../hooks/useAuth';
import { authApi } from '../api/authApi';
import { getAuthError } from '../utils/getAuthError';
import PasswordInput from './PasswordInput';

type Field = 'current_password' | 'new_password' | 'confirm_password';
type Errors = Partial<Record<Field, string>>;

const ChangePasswordForm: FC = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const currentPasswordRef = useRef<HTMLInputElement>(null);
  const newPasswordRef = useRef<HTMLInputElement>(null);
  const confirmPasswordRef = useRef<HTMLInputElement>(null);
  const [form, setForm] = useState<Record<Field, string>>({ current_password: '', new_password: '', confirm_password: '' });
  const [errors, setErrors] = useState<Errors>({});
  const [requestError, setRequestError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const update = (event: ChangeEvent<HTMLInputElement>) => {
    const field = event.target.name as Field;
    setForm((current) => ({ ...current, [field]: event.target.value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
    setRequestError('');
    setSuccess('');
  };

  const focusFirst = (next: Errors) => {
    if (next.current_password) currentPasswordRef.current?.focus();
    else if (next.new_password) newPasswordRef.current?.focus();
    else confirmPasswordRef.current?.focus();
  };

  const validate = (): Errors => {
    const next: Errors = {};
    if (!form.current_password) next.current_password = 'Current password is required';
    if (!form.new_password) next.new_password = 'New password is required';
    else if (form.new_password === form.current_password) next.new_password = 'New password must be different';
    if (!form.confirm_password) next.confirm_password = 'Please confirm your new password';
    else if (form.new_password !== form.confirm_password) next.confirm_password = 'Passwords do not match';
    return next;
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSubmitting) return;
    const nextErrors = validate();
    if (Object.keys(nextErrors).length) { setErrors(nextErrors); focusFirst(nextErrors); return; }
    setIsSubmitting(true);
    setRequestError('');
    try {
      const response = await authApi.changePassword(form);
      setForm({ current_password: '', new_password: '', confirm_password: '' });
      setSuccess(response.detail || 'Password changed successfully. Please sign in again.');
      window.setTimeout(() => { logout(); navigate('/login', { replace: true }); }, 2000);
    } catch (err) {
      const fieldErrors: Errors = {};
      if (axios.isAxiosError<Record<string, string | string[]>>(err) && err.response?.data) {
        for (const field of ['current_password', 'new_password', 'confirm_password'] as Field[]) {
          const value = err.response.data[field];
          if (value) fieldErrors[field] = Array.isArray(value) ? value.join(' ') : value;
        }
      }
      if (Object.keys(fieldErrors).length) { setErrors(fieldErrors); focusFirst(fieldErrors); }
      else setRequestError(getAuthError(err, 'Unable to change your password. Please try again.'));
    } finally { setIsSubmitting(false); }
  };

  return (
    <section aria-labelledby="change-password-heading" className="border-t border-border-default pt-8">
      <div className="mb-6">
        <h2 id="change-password-heading" className="text-2xl font-serif italic text-text-primary">Change password</h2>
        <p className="mt-2 text-sm text-text-secondary">Use a strong password you don’t use elsewhere. You’ll be asked to sign in again.</p>
      </div>
      <form className="space-y-5" onSubmit={handleSubmit} noValidate>
        <FormField label="Current password" id="current-password" error={errors.current_password} required>
          <PasswordInput ref={currentPasswordRef} id="current-password" name="current_password" autoComplete="current-password" value={form.current_password} onChange={update} error={errors.current_password} disabled={Boolean(success)} />
        </FormField>
        <div className="grid gap-5 sm:grid-cols-2">
          <FormField label="New password" id="new-password" error={errors.new_password} required>
            <PasswordInput ref={newPasswordRef} id="new-password" name="new_password" autoComplete="new-password" value={form.new_password} onChange={update} error={errors.new_password} disabled={Boolean(success)} />
          </FormField>
          <FormField label="Confirm new password" id="confirm-password" error={errors.confirm_password} required>
            <PasswordInput ref={confirmPasswordRef} id="confirm-password" name="confirm_password" autoComplete="new-password" value={form.confirm_password} onChange={update} error={errors.confirm_password} disabled={Boolean(success)} />
          </FormField>
        </div>
        {requestError && <Alert variant="error" message={requestError} />}
        {success && <Alert variant="success" message={success} />}
        <Button type="submit" size="lg" isLoading={isSubmitting} disabled={Boolean(success)}>Update password</Button>
      </form>
    </section>
  );
};

export default ChangePasswordForm;
