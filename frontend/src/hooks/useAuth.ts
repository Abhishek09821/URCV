import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '@/services/auth.service';
import { useAuthStore } from '@/store/auth.store';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useEffect } from 'react';

export function useAuth() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { setUser, clearAuth, isAuthenticated } = useAuthStore();

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authService.getCurrentUser,
    enabled: authService.isAuthenticated(),
    retry: false,
  });

  useEffect(() => {
    if (user) {
      setUser(user);
    }
  }, [user, setUser]);

  useEffect(() => {
    if (error) {
      clearAuth();
      navigate('/login');
    }
  }, [error, clearAuth, navigate]);

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: async () => {
      const user = await authService.getCurrentUser();
      setUser(user);
      queryClient.setQueryData(['auth', 'me'], user);
      toast.success('Welcome back!');
      navigate('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Login failed');
    },
  });

  const registerMutation = useMutation({
    mutationFn: authService.register,
    onSuccess: async (_, variables) => {
      toast.success('Registration successful! Please login.');
      // Auto-login after registration
      await loginMutation.mutateAsync({
        email: variables.email,
        password: variables.password,
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Registration failed');
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      clearAuth();
      queryClient.clear();
      toast.success('Logged out successfully');
      navigate('/login');
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }) =>
      authService.changePassword(currentPassword, newPassword),
    onSuccess: () => {
      toast.success('Password changed successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    },
  });

  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    changePassword: changePasswordMutation.mutate,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
  };
}
