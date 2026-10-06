import { HealthStatusResponse } from '@/types/health';
import {
  Company,
  CompanyCreate,
  Job,
  JobCreate,
  Candidate,
  CandidateCreate,
  Application,
  ApplicationCreate,
  Resume,
  UserProfile,
  UserRole,
  ScreeningResult,
} from '@/types/models';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiService {
  private static baseUrl = API_BASE_URL.replace(/\/$/, '');
  private static authToken: string | null = null;

  static setAuthToken(token: string | null) {
    this.authToken = token;
  }

  static getAuthToken(): string | null {
    return this.authToken;
  }

  private static getHeaders(extraHeaders: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = { ...extraHeaders };
    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }
    return headers;
  }

  static getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Authentication & Current User
   */
  static async getMe(): Promise<UserProfile> {
    const res = await fetch(`${this.baseUrl}/api/v1/auth/me`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Failed to fetch user profile (${res.status})`);
    }
    return res.json();
  }

  static async syncUser(name?: string): Promise<UserProfile> {
    const res = await fetch(`${this.baseUrl}/api/v1/auth/sync`, {
      method: 'POST',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ name }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Failed to sync user profile (${res.status})`);
    }
    return res.json();
  }

  static async signupUser(name: string, email: string, password: string): Promise<UserProfile> {
    const res = await fetch(`${this.baseUrl}/api/v1/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Registration failed (${res.status})`);
    }
    return res.json();
  }

  static async getUsers(): Promise<UserProfile[]> {
    const res = await fetch(`${this.baseUrl}/api/v1/auth/users`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) throw new Error(`Failed to list users (${res.status})`);
    return res.json();
  }

  static async updateUserRole(userId: string, role: UserRole): Promise<UserProfile> {
    const res = await fetch(`${this.baseUrl}/api/v1/auth/users/${userId}/role`, {
      method: 'PATCH',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ role }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to update user role');
    }
    return res.json();
  }

  /**
   * Health Probe
   */
  static async getHealth(): Promise<HealthStatusResponse> {
    const url = `${this.baseUrl}/api/v1/health`;
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: { Accept: 'application/json' },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown network error';
      return {
        status: 'unreachable',
        api: 'unavailable',
        database: 'unknown',
        environment: 'unknown',
        version: 'unknown',
        timestamp: new Date().toISOString(),
        database_error: `Failed to connect to ${url}: ${msg}`,
      };
    }
  }

  /**
   * Companies
   */
  static async getCompanies(): Promise<Company[]> {
    const res = await fetch(`${this.baseUrl}/api/v1/companies`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) throw new Error(`Failed to fetch companies (${res.status})`);
    return res.json();
  }

  static async createCompany(data: CompanyCreate): Promise<Company> {
    const res = await fetch(`${this.baseUrl}/api/v1/companies`, {
      method: 'POST',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to create company');
    }
    return res.json();
  }

  /**
   * Jobs
   */
  static async getJobs(companyId?: string): Promise<Job[]> {
    const query = companyId ? `?company_id=${companyId}` : '';
    const res = await fetch(`${this.baseUrl}/api/v1/jobs${query}`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) throw new Error(`Failed to fetch jobs (${res.status})`);
    return res.json();
  }

  static async createJob(data: JobCreate): Promise<Job> {
    const res = await fetch(`${this.baseUrl}/api/v1/jobs`, {
      method: 'POST',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to create job');
    }
    return res.json();
  }

  /**
   * Candidates
   */
  static async getCandidates(): Promise<Candidate[]> {
    const res = await fetch(`${this.baseUrl}/api/v1/candidates`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Failed to fetch candidates (${res.status})`);
    }
    return res.json();
  }

  static async getMyCandidateProfile(): Promise<Candidate> {
    const res = await fetch(`${this.baseUrl}/api/v1/candidates/me`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Failed to fetch candidate profile (${res.status})`);
    }
    return res.json();
  }

  static async createCandidate(data: CandidateCreate): Promise<Candidate> {
    const res = await fetch(`${this.baseUrl}/api/v1/candidates`, {
      method: 'POST',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to create candidate');
    }
    return res.json();
  }

  /**
   * Resume Upload
   */
  static async uploadResume(candidateId: string, file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${this.baseUrl}/api/v1/candidates/${candidateId}/resume`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to upload resume');
    }
    return res.json();
  }

  /**
   * Applications
   */
  static async getApplications(jobId?: string, candidateId?: string): Promise<Application[]> {
    const params = new URLSearchParams();
    if (jobId) params.append('job_id', jobId);
    if (candidateId) params.append('candidate_id', candidateId);
    const query = params.toString() ? `?${params.toString()}` : '';

    const res = await fetch(`${this.baseUrl}/api/v1/applications${query}`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) throw new Error(`Failed to fetch applications (${res.status})`);
    return res.json();
  }

  static async createApplication(data: ApplicationCreate): Promise<Application> {
    const res = await fetch(`${this.baseUrl}/api/v1/applications`, {
      method: 'POST',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to submit application');
    }
    return res.json();
  }

  /**
   * AI Screening (Phase 4)
   */
  static async triggerScreening(
    applicationId: string,
    forceRescreen: boolean = false,
    customNotes?: string
  ): Promise<ScreeningResult> {
    const res = await fetch(`${this.baseUrl}/api/v1/screenings/applications/${applicationId}`, {
      method: 'POST',
      headers: this.getHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ force_rescreen: forceRescreen, custom_notes: customNotes }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Screening evaluation failed (${res.status})`);
    }
    return res.json();
  }

  static async getScreeningForApplication(applicationId: string): Promise<ScreeningResult> {
    const res = await fetch(`${this.baseUrl}/api/v1/screenings/applications/${applicationId}`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Failed to fetch screening (${res.status})`);
    }
    return res.json();
  }

  static async getScreenings(jobId?: string): Promise<ScreeningResult[]> {
    const query = jobId ? `?job_id=${jobId}` : '';
    const res = await fetch(`${this.baseUrl}/api/v1/screenings${query}`, {
      headers: this.getHeaders(),
      cache: 'no-store',
    });
    if (!res.ok) throw new Error(`Failed to list screenings (${res.status})`);
    return res.json();
  }
}
