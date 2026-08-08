export interface Profile {
  id: number;
  email: string;
  username: string;
  role: string;
  phone_number: string | null;
  address: string | null;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  role: 'CLIENT';
  phone_number?: string;
  address?: string;
}

export interface RegisteredUser {
  email: string;
  role: RegisterCredentials['role'];
}
