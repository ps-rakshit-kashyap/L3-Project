export interface Company {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  name: string;
  description?: string;
}

export interface Job {
  id: string;
  company_id: string;
  title: string;
  description: string;
  requirements?: string | null;
  required_skills?: string | null;
  preferred_skills?: string | null;
  required_experience?: string | null;
  education_requirements?: string | null;
  location?: string | null;
  employment_type: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface JobCreate {
  company_id: string;
  title: string;
  description: string;
  requirements?: string;
  required_skills?: string;
  preferred_skills?: string;
  required_experience?: string;
  education_requirements?: string;
  location?: string;
  employment_type?: string;
  status?: string;
}

export interface Resume {
  id: string;
  candidate_id: string;
  file_name: string;
  file_path: string;
  file_type: string;
  uploaded_at: string;
  file_url?: string | null;
}

export interface Candidate {
  id: string;
  name: string;
  email: string;
  phone?: string | null;
  location?: string | null;
  profile_summary?: string | null;
  created_at: string;
  updated_at: string;
  resumes?: Resume[];
}

export interface CandidateCreate {
  name: string;
  email: string;
  phone?: string;
  location?: string;
  profile_summary?: string;
}

export interface Application {
  id: string;
  job_id: string;
  candidate_id: string;
  status: string;
  applied_at: string;
  updated_at: string;
}

export interface ApplicationCreate {
  job_id: string;
  candidate_id: string;
  status?: string;
}

export type UserRole = 'ADMIN' | 'RECRUITER' | 'CANDIDATE';

export interface UserProfile {
  id: string;
  auth_user_id: string | null;
  name: string;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export type ScreeningRecommendation = 'ADVANCE' | 'HOLD' | 'REJECT';

export interface SkillMatch {
  skill: string;
  category: 'required' | 'preferred';
  matched: boolean;
  evidence?: string | null;
}

export interface ScreeningEvaluation {
  overall_score: number;
  recommendation: ScreeningRecommendation;
  passed: boolean;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  skills_analysis: SkillMatch[];
  experience_assessment: string;
  education_assessment: string;
  recommended_interview_questions: string[];
}

export interface ScreeningResult {
  id: string;
  application_id: string;
  score: number | null;
  recommendation: string | null;
  passed: boolean | null;
  summary: string | null;
  details: ScreeningEvaluation | null;
  created_at: string;
  updated_at: string;
}


