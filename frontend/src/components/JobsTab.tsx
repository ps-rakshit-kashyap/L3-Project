'use client';

import React, { useState, useEffect } from 'react';
import { ApiService } from '@/services/api';
import { Job, Company } from '@/types/models';
import { Briefcase, Plus, Loader2, AlertCircle } from 'lucide-react';

export const JobsTab: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [companyId, setCompanyId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState('');
  const [location, setLocation] = useState('Remote');
  const [employmentType, setEmploymentType] = useState('Full-time');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [jobsData, companiesData] = await Promise.all([
        ApiService.getJobs(),
        ApiService.getCompanies(),
      ]);
      setJobs(jobsData);
      setCompanies(companiesData);
      if (companiesData.length > 0 && !companyId) {
        setCompanyId(companiesData[0].id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs or companies');
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyId || !title.trim() || !description.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await ApiService.createJob({
        company_id: companyId,
        title: title.trim(),
        description: description.trim(),
        requirements: requirements.trim() || undefined,
        location: location.trim() || undefined,
        employment_type: employmentType,
        status: 'open',
      });
      setTitle('');
      setDescription('');
      setRequirements('');
      await fetchData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create job');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Create Job Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
          <Briefcase size={20} color="var(--accent-sky)" />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Create New Job Posting</h3>
        </div>

        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--status-error-bg)', color: 'var(--status-error)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleCreate}>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="job-company">Hiring Company *</label>
              <select
                id="job-company"
                className="form-select"
                value={companyId}
                onChange={(e) => setCompanyId(e.target.value)}
                required
              >
                <option value="">-- Select Company --</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="job-title">Job Title *</label>
              <input
                id="job-title"
                className="form-input"
                placeholder="e.g. Senior Machine Learning Engineer"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="job-location">Location</label>
              <input
                id="job-location"
                className="form-input"
                placeholder="e.g. Remote / San Francisco"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="job-type">Employment Type</label>
              <select
                id="job-type"
                className="form-select"
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
              >
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="job-desc">Job Description *</label>
            <textarea
              id="job-desc"
              className="form-textarea"
              placeholder="Describe core role responsibilities..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="job-reqs">Requirements</label>
            <input
              id="job-reqs"
              className="form-input"
              placeholder="e.g. Python, PyTorch, LangChain, 5+ yrs experience"
              value={requirements}
              onChange={(e) => setRequirements(e.target.value)}
            />
          </div>

          <button
            type="submit"
            id="btn-create-job"
            className="btn-primary"
            disabled={submitting || companies.length === 0}
          >
            {submitting ? <Loader2 size={16} className="spin" /> : <Plus size={16} />}
            <span>{submitting ? 'Creating...' : 'Post Job'}</span>
          </button>
          {companies.length === 0 && (
            <span style={{ fontSize: '0.8rem', color: 'var(--status-degraded)', marginLeft: '1rem' }}>
              Create a company first in the Companies tab.
            </span>
          )}
        </form>
      </div>

      {/* Jobs List */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Active Job Postings ({jobs.length})</h3>
          <button onClick={fetchData} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
            Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading jobs...</div>
        ) : jobs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No jobs posted yet. Create your first job posting above.
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Company ID</th>
                  <th>Location</th>
                  <th>Type</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((j) => (
                  <tr key={j.id}>
                    <td style={{ fontWeight: 600 }}>{j.title}</td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--accent-sky)' }}>
                      {j.company_id.substring(0, 8)}...
                    </td>
                    <td>{j.location || 'Remote'}</td>
                    <td>{j.employment_type}</td>
                    <td>
                      <span className="status-pill healthy" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>
                        {j.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
