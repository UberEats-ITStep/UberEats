import apiClient from '../../../api/client';
import type {
  AuthTokens,
  ChangePasswordData,
  DetailResponse,
  LoginCredentials,
  Profile,
  RegisterCredentials,
  ResetPasswordData,
  RegisteredUser,
} from '../types/auth.types';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>('/auth/login/', credentials);
    return response.data;
  },

  register: async (credentials: RegisterCredentials): Promise<RegisteredUser> => {
    const response = await apiClient.post<RegisteredUser>('/auth/register/', credentials);
    return response.data;
  },

  getProfile: async (): Promise<Profile> => {
    const response = await apiClient.get<Profile>('/profile/');
    return response.data;
  },

  verifyEmail: async (email: string, code: string): Promise<AuthTokens> => {
    const response = await apiClient.post<AuthTokens>('/auth/verify-email/', { email, code });
    return response.data;
  },

  resendVerification: async (email: string): Promise<void> => {
    await apiClient.post('/auth/resend-verification/', { email });
  },

  forgotPassword: async (email: string): Promise<DetailResponse> => {
    const response = await apiClient.post<DetailResponse>('/auth/forgot-password/', { email });
    return response.data;
  },

  resetPassword: async (data: ResetPasswordData): Promise<DetailResponse> => {
    const response = await apiClient.post<DetailResponse>('/auth/reset-password/', data);
    return response.data;
  },

  changePassword: async (data: ChangePasswordData): Promise<DetailResponse> => {
    const response = await apiClient.post<DetailResponse>('/auth/change-password/', data);
    return response.data;
  },
};
