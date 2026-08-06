// Core types for URCV frontend

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

// Resume Types
export interface ResumePersonalInfo {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  portfolio?: string;
}

export interface ResumeEducation {
  institution: string;
  degree: string;
  field?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  location?: string;
  description?: string;
}

export interface ResumeExperience {
  company: string;
  position: string;
  start_date?: string;
  end_date?: string;
  location?: string;
  description: string[];
  is_current?: boolean;
}

export interface ResumeProject {
  name: string;
  description: string[];
  technologies?: string[];
  url?: string;
  start_date?: string;
  end_date?: string;
}

export interface ResumeCertification {
  name: string;
  issuer: string;
  date?: string;
  url?: string;
}

export interface ResumeAchievement {
  title: string;
  description?: string;
  date?: string;
}

export interface ResumeSkills {
  languages?: string[];
  frameworks?: string[];
  tools?: string[];
  databases?: string[];
  other?: string[];
}

export interface ResumeData {
  personal?: ResumePersonalInfo;
  summary?: string;
  education?: ResumeEducation[];
  experience?: ResumeExperience[];
  projects?: ResumeProject[];
  skills?: ResumeSkills;
  certifications?: ResumeCertification[];
  achievements?: ResumeAchievement[];
}

export interface Resume {
  id: string;
  user_id: string;
  original_filename: string;
  file_url: string;
  resume_data: ResumeData;
  confidence_score: number;
  is_verified: boolean;
  ats_score?: number;
  ats_analysis?: ATSAnalysis;
  created_at: string;
  updated_at: string;
}

// ATS Analysis Types
export interface ATSCategoryScore {
  score: number;
  max_score: number;
  details: string[];
}

export interface ATSAnalysis {
  overall_score: number;
  categories: {
    contact_information: ATSCategoryScore;
    section_structure: ATSCategoryScore;
    formatting: ATSCategoryScore;
    keywords: ATSCategoryScore;
    readability: ATSCategoryScore;
    file_structure: ATSCategoryScore;
  };
  suggestions: ATSSuggestion[];
  keywords_found: string[];
  keywords_missing: string[];
}

export interface ATSSuggestion {
  category: string;
  priority: 'high' | 'medium' | 'low';
  suggestion: string;
  impact: string;
}

// AI Improvement Types
export interface AIImprovement {
  id: string;
  resume_id: string;
  section_type: string;
  section_index?: number;
  original_content: string;
  improved_content: string;
  improvement_type: string;
  is_applied: boolean;
  created_at: string;
}

export interface AIImprovementRequest {
  section_type: 'summary' | 'experience' | 'projects' | 'achievements';
  section_index?: number;
  improvement_types: string[];
}

// Export Types
export interface ExportRequest {
  format: 'pdf' | 'docx';
  template_id?: string;
}

export interface ExportHistory {
  id: string;
  resume_id: string;
  format: string;
  template_id?: string;
  file_url: string;
  created_at: string;
}

// Template Types
export interface Template {
  id: string;
  name: string;
  description: string;
  preview_url?: string;
  is_premium: boolean;
  category: string;
}

// Job Description Types
export interface JobDescription {
  id: string;
  user_id: string;
  title: string;
  company: string;
  description: string;
  required_skills: string[];
  created_at: string;
}

export interface JDMatch {
  id: string;
  resume_id: string;
  jd_id: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  suggestions: string[];
  created_at: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// UI State Types
export type ThemeMode = 'light' | 'dark';

export interface AppSettings {
  theme: ThemeMode;
  language: string;
  notifications: boolean;
}
