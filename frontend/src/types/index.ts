export interface User {
  id: number;
  email: string;
  role: 'Client' | 'Courier' | 'Admin';
}
