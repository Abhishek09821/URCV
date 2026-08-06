import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { resumeService } from '@/services/resume.service';
import { useResumeStore } from '@/store/resume.store';
import toast from 'react-hot-toast';
import { useEffect } from 'react';
import type { ResumeData } from '@/types';

export function useResumes(page = 1, size = 20) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['resumes', page, size],
    queryFn: () => resumeService.listResumes(page, size),
  });

  return {
    resumes: data?.items || [],
    total: data?.total || 0,
    pages: data?.pages || 0,
    isLoading,
    error,
  };
}

export function useResume(id: string | undefined) {
  const { setCurrentResume } = useResumeStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['resume', id],
    queryFn: () => resumeService.getResume(id!),
    enabled: !!id,
  });

  useEffect(() => {
    if (data) {
      setCurrentResume(data);
    }
  }, [data, setCurrentResume]);

  return {
    resume: data,
    isLoading,
    error,
  };
}

export function useUploadResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: resumeService.uploadResume,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      toast.success('Resume uploaded successfully!');
      return data;
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload resume');
    },
  });
}

export function useUpdateResume(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<ResumeData>) => resumeService.updateResume(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resume', id] });
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      toast.success('Resume updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update resume');
    },
  });
}

export function useDeleteResume() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: resumeService.deleteResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      toast.success('Resume deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete resume');
    },
  });
}

export function useVerifyResume(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => resumeService.verifyResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resume', id] });
      queryClient.invalidateQueries({ queryKey: ['resumes'] });
      toast.success('Resume verified!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to verify resume');
    },
  });
}
