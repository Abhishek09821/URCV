import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/config';
import type { ExportRequest, ExportHistory } from '@/types';

export const exportService = {
  async exportResume(resumeId: string, request: ExportRequest): Promise<{ file_url: string }> {
    const response = await apiClient.post(API_ENDPOINTS.EXPORT.EXPORT(resumeId), request);
    return response.data;
  },

  async getExportHistory(resumeId: string): Promise<ExportHistory[]> {
    const response = await apiClient.get(API_ENDPOINTS.EXPORT.HISTORY(resumeId));
    return response.data;
  },
};
