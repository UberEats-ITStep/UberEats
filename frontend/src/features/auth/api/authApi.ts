import apiClient from '../../../api/client';
import type {
  AuthTokens,
  LoginCredentials,
  Profile,
  RegisterCredentials,
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
};
