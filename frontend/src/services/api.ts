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
} from '@/types/models';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiService {
  private static baseUrl = API_BASE_URL.replace(/\/$/, '');

  static getBaseUrl(): string {
    return this.baseUrl;
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
    const res = await fetch(`${this.baseUrl}/api/v1/companies`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch companies (${res.status})`);
    return res.json();
  }

  static async createCompany(data: CompanyCreate): Promise<Company> {
    const res = await fetch(`${this.baseUrl}/api/v1/companies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
    const res = await fetch(`${this.baseUrl}/api/v1/jobs${query}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch jobs (${res.status})`);
    return res.json();
  }

  static async createJob(data: JobCreate): Promise<Job> {
    const res = await fetch(`${this.baseUrl}/api/v1/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
    const res = await fetch(`${this.baseUrl}/api/v1/candidates`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch candidates (${res.status})`);
    return res.json();
  }

  static async createCandidate(data: CandidateCreate): Promise<Candidate> {
    const res = await fetch(`${this.baseUrl}/api/v1/candidates`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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

    const res = await fetch(`${this.baseUrl}/api/v1/applications${query}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Failed to fetch applications (${res.status})`);
    return res.json();
  }

  static async createApplication(data: ApplicationCreate): Promise<Application> {
    const res = await fetch(`${this.baseUrl}/api/v1/applications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to submit application');
    }
    return res.json();
  }
}
