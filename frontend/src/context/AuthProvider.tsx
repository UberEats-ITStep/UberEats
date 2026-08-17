import { useCallback, useEffect, useState } from 'react';
import type { FC, ReactNode } from 'react';
import { authApi } from '../features/auth/api/authApi';
import type {
  LoginCredentials,
  Profile,
  RegisterCredentials,
} from '../features/auth/types/auth.types';
import { AuthContext } from './AuthContext';
import { AUTH_LOGOUT_EVENT } from '../api/client';

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setProfile(null);
  }, []);

  useEffect(() => {
    window.addEventListener(AUTH_LOGOUT_EVENT, clearSession);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, clearSession);
  }, [clearSession]);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const currentProfile = await authApi.getProfile();
          setProfile(currentProfile);
        } catch {
          clearSession();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, [clearSession]);

  const login = async (credentials: LoginCredentials) => {
    const { access, refresh } = await authApi.login(credentials);
    await loginWithTokens(access, refresh);
  };

  const loginWithTokens = async (access: string, refresh: string) => {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    try {
      const currentProfile = await authApi.getProfile();
      setProfile(currentProfile);
    } catch (error) {
      clearSession();
      throw error;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    await authApi.register(credentials);
  };

  const logout = () => {
    clearSession();
  };

  return (
    <AuthContext.Provider
      value={{
        profile,
        isAuthenticated: profile !== null,
        isLoading,
        login,
        loginWithTokens,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
