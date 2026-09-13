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
import { signInWithGoogle, signOutFromFirebase } from '../features/auth/firebase';

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

  const loginWithGoogle = async () => {
    const idToken = await signInWithGoogle();
    try {
      const { access, refresh } = await authApi.loginWithFirebase(idToken);
      await loginWithTokens(access, refresh);
    } catch (error) {
      await signOutFromFirebase();
      throw error;
    }
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

  const logout = async () => {
    clearSession();
    try {
      await signOutFromFirebase();
    } catch {
      // The local Django session is already cleared. Firebase will retry its
      // persisted state synchronization when connectivity returns.
    }
  };

  const refreshProfile = async () => {
    const currentProfile = await authApi.getProfile();
    setProfile(currentProfile);
    return currentProfile;
  };

  return (
    <AuthContext.Provider
      value={{
        profile,
        isAuthenticated: profile !== null,
        isLoading,
        login,
        loginWithGoogle,
        loginWithTokens,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
