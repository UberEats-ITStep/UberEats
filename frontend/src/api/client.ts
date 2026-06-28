import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (simplified for now)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Refresh logic will be implemented later
    if (error.response?.status === 401) {
      console.warn('Unauthorized access. Token may be invalid or expired.');
      // Optionally could clear token and redirect to login, but leaving minimal for now.
    }
    return Promise.reject(error);
  }
);

export default apiClient;
