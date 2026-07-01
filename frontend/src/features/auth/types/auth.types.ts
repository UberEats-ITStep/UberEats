export interface User {
  id: number;
  email: string;
  username: string;
  role: 'Client' | 'Courier' | 'Admin';
}

export interface AuthResponse {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}
