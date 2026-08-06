import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/config';
import type { ATSAnalysis } from '@/types';

export const atsService = {
  async analyzeResume(resumeId: string): Promise<ATSAnalysis> {
    const response = await apiClient.post(API_ENDPOINTS.ATS.ANALYZE(resumeId));
    return response.data;
  },
};
