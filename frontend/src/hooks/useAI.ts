import { useMutation, useQueryClient } from '@tanstack/react-query';
import { aiService } from '@/services/ai.service';
import toast from 'react-hot-toast';
import type { AIImprovementRequest } from '@/types';

export function useImproveSection(resumeId: string) {
  return useMutation({
    mutationFn: (request: AIImprovementRequest) => aiService.improveSection(resumeId, request),
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to generate improvement');
    },
  });
}

export function useApplyImprovement(resumeId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (improvementId: string) => aiService.applyImprovement(improvementId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resume', resumeId] });
      toast.success('Improvement applied!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to apply improvement');
    },
  });
}
