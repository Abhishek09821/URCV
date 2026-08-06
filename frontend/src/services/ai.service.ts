import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/config';
import type { AIImprovement, AIImprovementRequest } from '@/types';

export const aiService = {
  async improveSection(resumeId: string, request: AIImprovementRequest): Promise<AIImprovement> {
    const response = await apiClient.post(API_ENDPOINTS.AI.IMPROVE(resumeId), request);
    return response.data;
  },

  async applyImprovement(improvementId: string): Promise<void> {
    await apiClient.post(API_ENDPOINTS.AI.APPLY(improvementId));
  },
};
