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
  AvatarOption, DeliveryAddress, DeliveryAddressInput, ProfileUpdate,
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

  updateProfile: async (data: ProfileUpdate): Promise<Profile> => {
    const response = await apiClient.patch<Profile>('/profile/', data);
    return response.data;
  },
  getAvatarOptions: async (): Promise<AvatarOption[]> => {
    const response = await apiClient.get<{ avatars: AvatarOption[] }>('/profile/avatar-options/');
    return response.data.avatars;
  },
  getAddresses: async (): Promise<DeliveryAddress[]> => {
    const response = await apiClient.get<DeliveryAddress[]>('/profile/addresses/');
    return response.data;
  },
  createAddress: async (data: DeliveryAddressInput): Promise<DeliveryAddress> => {
    const response = await apiClient.post<DeliveryAddress>('/profile/addresses/', data);
    return response.data;
  },
  updateAddress: async (id: number, data: DeliveryAddressInput): Promise<DeliveryAddress> => {
    const response = await apiClient.patch<DeliveryAddress>(`/profile/addresses/${id}/`, data);
    return response.data;
  },
  deleteAddress: async (id: number): Promise<void> => { await apiClient.delete(`/profile/addresses/${id}/`); },
  setDefaultAddress: async (id: number): Promise<DeliveryAddress> => {
    const response = await apiClient.post<DeliveryAddress>(`/profile/addresses/${id}/set-default/`);
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
