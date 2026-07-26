import { useState } from "react";
import type { FC, FormEvent, ChangeEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../hooks/useAuth";
import { getAuthError } from "../utils/getAuthError";

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
    <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg border border-gray-100">
      <div className="text-center">
        <h2 className="text-3xl font-extrabold text-gray-900">
          Create an account
        </h2>
        <p className="mt-2 text-sm text-gray-600">Join UberEats today.</p>
      </div>

      <form className="mt-8 space-y-5" onSubmit={handleRegister} noValidate>
        <div className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
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
                  errors.email
                    ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                    : "border-gray-300 focus:ring-green-500 focus:border-green-500"
                } rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm`}
                placeholder="you@example.com"
              />
              {errors.email && (
                <p className="mt-2 text-sm text-red-600">{errors.email}</p>
              )}
            </div>
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <div className="mt-1">
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                value={formData.password}
                onChange={handleChange}
                className={`appearance-none block w-full px-3 py-2 border ${
                  errors.password
                    ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                    : "border-gray-300 focus:ring-green-500 focus:border-green-500"
                } rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-2 text-sm text-red-600">{errors.password}</p>
              )}
            </div>
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-gray-700"
            >
              Confirm Password
            </label>
            <div className="mt-1">
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                className={`appearance-none block w-full px-3 py-2 border ${
                  errors.confirmPassword
                    ? "border-red-300 focus:ring-red-500 focus:border-red-500"
                    : "border-gray-300 focus:ring-green-500 focus:border-green-500"
                } rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm`}
                placeholder="••••••••"
              />
              {errors.confirmPassword && (
                <p className="mt-2 text-sm text-red-600">
                  {errors.confirmPassword}
                </p>
              )}
            </div>
          </div>

          <div>
            <label
              htmlFor="phoneNumber"
              className="block text-sm font-medium text-gray-700"
            >
              Phone number <span className="font-normal text-gray-400">(optional)</span>
            </label>
            <div className="mt-1">
              <input
                id="phoneNumber"
                name="phoneNumber"
                type="tel"
                autoComplete="tel"
                value={formData.phoneNumber}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 focus:ring-green-500 focus:border-green-500 rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm"
                placeholder="+380 00 000 0000"
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="address"
              className="block text-sm font-medium text-gray-700"
            >
              Address <span className="font-normal text-gray-400">(optional)</span>
            </label>
            <div className="mt-1">
              <input
                id="address"
                name="address"
                type="text"
                autoComplete="street-address"
                value={formData.address}
                onChange={handleChange}
                className="appearance-none block w-full px-3 py-2 border border-gray-300 focus:ring-green-500 focus:border-green-500 rounded-md shadow-sm placeholder-gray-400 focus:outline-none sm:text-sm"
                placeholder="Delivery address"
              />
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
            {isSubmitting ? "Creating account..." : "Sign up"}
          </button>
        </div>
      </form>

      <div className="text-center text-sm">
        <span className="text-gray-600">Already have an account? </span>
        <Link
          to="/login"
          className="font-medium text-green-600 hover:text-green-500 transition-colors"
        >
          Log in
        </Link>
      </div>
    </div>
  );
};

export default RegisterForm;
