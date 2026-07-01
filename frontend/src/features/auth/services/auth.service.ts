import apiClient from '../../../api/client';
import type { AuthResponse, LoginCredentials, User } from '../types/auth.types';

export const authService = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login/', credentials);
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/profile/');
    return response.data;
  },
};
