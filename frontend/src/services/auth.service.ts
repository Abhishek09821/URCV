import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS, APP_CONFIG } from '@/lib/config';
import type { User, AuthTokens, LoginRequest, RegisterRequest } from '@/types';

export const authService = {
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, data);
    return response.data;
  },

  async login(data: LoginRequest): Promise<AuthTokens> {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, data);
    const tokens = response.data;
    localStorage.setItem(APP_CONFIG.TOKEN_STORAGE_KEY, JSON.stringify(tokens));
    return tokens;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } finally {
      localStorage.removeItem(APP_CONFIG.TOKEN_STORAGE_KEY);
    }
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get(API_ENDPOINTS.AUTH.ME);
    return response.data;
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  getStoredTokens(): AuthTokens | null {
    const tokensStr = localStorage.getItem(APP_CONFIG.TOKEN_STORAGE_KEY);
    return tokensStr ? JSON.parse(tokensStr) : null;
  },

  isAuthenticated(): boolean {
    return !!this.getStoredTokens();
  },
};
