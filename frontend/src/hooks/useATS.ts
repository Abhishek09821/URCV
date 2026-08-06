import { useMutation, useQueryClient } from '@tanstack/react-query';
import { atsService } from '@/services/ats.service';
import toast from 'react-hot-toast';

export function useAnalyzeATS(resumeId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => atsService.analyzeResume(resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resume', resumeId] });
      toast.success('ATS analysis complete!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'ATS analysis failed');
    },
  });
}
