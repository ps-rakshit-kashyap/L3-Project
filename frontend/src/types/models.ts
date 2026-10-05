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
