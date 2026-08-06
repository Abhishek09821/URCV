import { useMutation, useQuery } from '@tanstack/react-query';
import { exportService } from '@/services/export.service';
import { downloadFile } from '@/lib/utils';
import toast from 'react-hot-toast';
import type { ExportRequest } from '@/types';

export function useExportResume(resumeId: string) {
  return useMutation({
    mutationFn: (request: ExportRequest) => exportService.exportResume(resumeId, request),
    onSuccess: (data) => {
      toast.success('Export ready! Downloading...');
      downloadFile(data.file_url, `resume_${Date.now()}.pdf`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Export failed');
    },
  });
}

export function useExportHistory(resumeId: string) {
  return useQuery({
    queryKey: ['export-history', resumeId],
    queryFn: () => exportService.getExportHistory(resumeId),
    enabled: !!resumeId,
  });
}
