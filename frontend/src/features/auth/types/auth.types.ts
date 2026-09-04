export interface Profile {
  id: number;
  email: string;
  username: string;
  role: string;
  phone_number: string | null;
  address: string | null;
  avatar: string;
  default_address: DeliveryAddress | null;
}

export interface AvatarOption { id: string; label: string; }

export interface DeliveryAddress {
  id: number; label: string; formatted_address: string; street: string; building: string;
  apartment: string; entrance: string; floor: number | null; delivery_notes: string;
  contact_phone: string; latitude: string | null; longitude: string | null;
  is_default: boolean; created_at: string; updated_at: string;
}

export type DeliveryAddressInput = Omit<DeliveryAddress, 'id' | 'is_default' | 'created_at' | 'updated_at'>;
export type ProfileUpdate = Pick<Profile, 'phone_number' | 'avatar'>;

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

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ResetPasswordData {
  email: string;
  verification_code: string;
  new_password: string;
  confirm_password: string;
}

export interface DetailResponse {
  detail: string;
}
