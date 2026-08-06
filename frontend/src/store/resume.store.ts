import { create } from 'zustand';
import type { Resume } from '@/types';

interface ResumeState {
  currentResume: Resume | null;
  setCurrentResume: (resume: Resume | null) => void;
  updateCurrentResumeData: (data: Resume['resume_data']) => void;
}

export const useResumeStore = create<ResumeState>((set) => ({
  currentResume: null,
  setCurrentResume: (resume) => set({ currentResume: resume }),
  updateCurrentResumeData: (data) =>
    set((state) => ({
      currentResume: state.currentResume
        ? { ...state.currentResume, resume_data: data }
        : null,
    })),
}));
