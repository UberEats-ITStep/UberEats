import { useEffect, useState } from 'react';
import type { FC, ReactNode } from 'react';
import { authApi } from '../features/auth/api/authApi';
import type {
  LoginCredentials,
  Profile,
  RegisterCredentials,
} from '../features/auth/types/auth.types';
import { AuthContext } from './AuthContext';

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const currentProfile = await authApi.getProfile();
          setProfile(currentProfile);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const { access, refresh } = await authApi.login(credentials);
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    try {
      const currentProfile = await authApi.getProfile();
      setProfile(currentProfile);
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      throw error;
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    await authApi.register(credentials);
    await login({ email: credentials.email, password: credentials.password });
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setProfile(null);
  };

  return (
    <AuthContext.Provider
      value={{
        profile,
        isAuthenticated: profile !== null,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
