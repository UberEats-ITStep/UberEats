import axios from 'axios';
import type { AxiosError, InternalAxiosRequestConfig } from 'axios';

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

interface RefreshResponse {
  access: string;
  refresh?: string;
}

export const AUTH_LOGOUT_EVENT = 'auth:logout';

const PUBLIC_AUTH_PATHS = new Set([
  '/auth/login/',
  '/auth/register/',
  '/auth/firebase/',
  '/auth/refresh/',
  '/auth/verify-email/',
  '/auth/resend-verification/',
  '/auth/forgot-password/',
  '/auth/reset-password/',
]);

const PUBLIC_READ_PATHS = [
  '/restaurants',
  '/cuisines',
  '/categories',
  '/menu-items',
  '/menuItems',
];

const getPath = (url?: string) => url?.split('?')[0];

const isPublicAuthPath = (url?: string) => {
  const path = getPath(url);
  return path ? PUBLIC_AUTH_PATHS.has(path) : false;
};

const isPublicRequest = (config: Pick<InternalAxiosRequestConfig, 'url' | 'method'>) => {
  if (isPublicAuthPath(config.url)) {
    return true;
  }

  const path = getPath(config.url);
  if (!path || (config.method ?? 'get').toLowerCase() !== 'get') {
    return false;
  }
  return PUBLIC_READ_PATHS.some((prefix) => path === prefix || path.startsWith(`${prefix}/`));
};

const apiBaseUrl = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api').replace(/\/+$/, '');

const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers && !isPublicRequest(config)) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const request = error.config as RetryableRequestConfig | undefined;

    if (
      error.response?.status !== 401 ||
      !request ||
      request._retry ||
      isPublicAuthPath(request.url)
    ) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
      return Promise.reject(error);
    }

    request._retry = true;

    try {
      const tokens = await refreshTokens(refreshToken);
      localStorage.setItem('access_token', tokens.access);
      if (tokens.refresh) {
        localStorage.setItem('refresh_token', tokens.refresh);
      }
      request.headers.Authorization = `Bearer ${tokens.access}`;
      return apiClient(request);
    } catch (refreshError) {
      window.dispatchEvent(new Event(AUTH_LOGOUT_EVENT));
      return Promise.reject(refreshError);
    }
  }
);

let refreshRequest: Promise<RefreshResponse> | null = null;

const refreshTokens = (refreshToken: string): Promise<RefreshResponse> => {
  if (!refreshRequest) {
    refreshRequest = axios
      .post<RefreshResponse>(
        `${apiBaseUrl}/auth/refresh/`,
        { refresh: refreshToken },
        { headers: { 'Content-Type': 'application/json' } },
      )
      .then(({ data }) => data)
      .finally(() => {
        refreshRequest = null;
      });
  }

  return refreshRequest;
};

export default apiClient;
