import axios from 'axios';

type ApiErrorData = Record<string, string | string[]> & { detail?: string };

export const getAuthError = (error: unknown, fallback: string): string => {
  if (!axios.isAxiosError<ApiErrorData>(error) || !error.response?.data) {
    return fallback;
  }

  const data = error.response.data;
  if (Array.isArray(data.email) && data.email.some((message) => message.includes('already exists'))) {
    return 'An account with this email already exists.';
  }

  if (typeof data.detail === 'string') {
    return data.detail;
  }

  const firstMessage = Object.values(data)[0];
  return Array.isArray(firstMessage) ? firstMessage[0] : firstMessage || fallback;
};
