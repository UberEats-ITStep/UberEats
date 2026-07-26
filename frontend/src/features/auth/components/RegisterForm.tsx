import { useState } from "react";
import type { FC, FormEvent, ChangeEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../hooks/useAuth";
import { getAuthError } from "../utils/getAuthError";
import { Card, FormField, Input, Button, Alert } from "../../../components/common";

const RegisterForm: FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    phoneNumber: "",
    address: "",
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [requestError, setRequestError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters long";
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setRequestError("");
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    setRequestError("");

    try {
      await register({
        email: formData.email,
        password: formData.password,
        role: "CLIENT",
        phone_number: formData.phoneNumber.trim() || undefined,
        address: formData.address.trim() || undefined,
      });
      navigate("/", { replace: true });
    } catch (error) {
      setRequestError(getAuthError(error, "Unable to create your account. Please try again."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card elevation="elevated" padding="lg" className="w-full max-w-md space-y-6">
      <div className="text-center">
        <h2 className="text-page-title">
          Create an account
        </h2>
        <p className="mt-2 text-body">Join BiteUp today.</p>
      </div>

      <form className="mt-8 space-y-5" onSubmit={handleRegister} noValidate>
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
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              placeholder="••••••••"
            />
          </FormField>

          <FormField label="Confirm Password" id="confirmPassword" error={errors.confirmPassword} required>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              placeholder="••••••••"
            />
          </FormField>

          <FormField label="Phone number" id="phoneNumber" optionalLabel>
            <Input
              id="phoneNumber"
              name="phoneNumber"
              type="tel"
              autoComplete="tel"
              value={formData.phoneNumber}
              onChange={handleChange}
              placeholder="+380 00 000 0000"
            />
          </FormField>

          <FormField label="Address" id="address" optionalLabel>
            <Input
              id="address"
              name="address"
              type="text"
              autoComplete="street-address"
              value={formData.address}
              onChange={handleChange}
              placeholder="Delivery address"
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
            Sign up
          </Button>
        </div>
      </form>

      <div className="text-center text-sm text-text-secondary">
        <span>Already have an account? </span>
        <Link
          to="/login"
          className="font-semibold text-primary transition-base hover:text-accent"
        >
          Log in
        </Link>
      </div>
    </Card>
  );
};

export default RegisterForm;
