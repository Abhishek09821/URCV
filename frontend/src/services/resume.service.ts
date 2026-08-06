import { apiClient } from '@/lib/api-client';
import { API_ENDPOINTS } from '@/lib/config';
import type { Resume, ResumeData, PaginatedResponse } from '@/types';

export const resumeService = {
  async uploadResume(file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(API_ENDPOINTS.RESUMES.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async listResumes(page = 1, size = 20): Promise<PaginatedResponse<Resume>> {
    const response = await apiClient.get(API_ENDPOINTS.RESUMES.LIST, {
      params: { page, size },
    });
    return response.data;
  },

  async getResume(id: string): Promise<Resume> {
    const response = await apiClient.get(API_ENDPOINTS.RESUMES.DETAIL(id));
    return response.data;
  },

  async updateResume(id: string, data: Partial<ResumeData>): Promise<Resume> {
    const response = await apiClient.put(API_ENDPOINTS.RESUMES.UPDATE(id), {
      resume_data: data,
    });
    return response.data;
  },

  async deleteResume(id: string): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.RESUMES.DELETE(id));
  },

  async verifyResume(id: string): Promise<Resume> {
    const response = await apiClient.post(API_ENDPOINTS.RESUMES.VERIFY(id));
    return response.data;
  },
};
