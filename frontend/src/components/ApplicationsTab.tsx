'use client';

import React, { useState, useEffect } from 'react';
import { ApiService } from '@/services/api';
import { Application, Job, Candidate } from '@/types/models';
import { Send, Plus, Loader2, AlertCircle } from 'lucide-react';

export const ApplicationsTab: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);

  const [jobId, setJobId] = useState('');
  const [candidateId, setCandidateId] = useState('');
  const [status, setStatus] = useState('applied');

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [appsData, jobsData, candidatesData] = await Promise.all([
        ApiService.getApplications(),
        ApiService.getJobs(),
        ApiService.getCandidates(),
      ]);
      setApplications(appsData);
      setJobs(jobsData);
      setCandidates(candidatesData);

      if (jobsData.length > 0 && !jobId) setJobId(jobsData[0].id);
      if (candidatesData.length > 0 && !candidateId) setCandidateId(candidatesData[0].id);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load applications data');
    } finally {
      setLoading(false);
    }
  }, [jobId, candidateId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobId || !candidateId) return;
    setSubmitting(true);
    setError(null);
    try {
      await ApiService.createApplication({
        job_id: jobId,
        candidate_id: candidateId,
        status: status,
      });
      await fetchData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create application');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Create Application Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
          <Send size={20} color="var(--accent-sky)" />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Create Job Application</h3>
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
              <label className="form-label" htmlFor="app-job">Target Job *</label>
              <select
                id="app-job"
                className="form-select"
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                required
              >
                <option value="">-- Select Job --</option>
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title} ({j.location || 'Remote'})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="app-candidate">Candidate *</label>
              <select
                id="app-candidate"
                className="form-select"
                value={candidateId}
                onChange={(e) => setCandidateId(e.target.value)}
                required
              >
                <option value="">-- Select Candidate --</option>
                {candidates.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.email})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="app-status">Status</label>
              <select
                id="app-status"
                className="form-select"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="applied">applied</option>
                <option value="screening">screening</option>
                <option value="interviewed">interviewed</option>
                <option value="offered">offered</option>
                <option value="rejected">rejected</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            id="btn-create-app"
            className="btn-primary"
            disabled={submitting || jobs.length === 0 || candidates.length === 0}
          >
            {submitting ? <Loader2 size={16} className="spin" /> : <Plus size={16} />}
            <span>{submitting ? 'Submitting...' : 'Link Candidate to Job'}</span>
          </button>
          {(jobs.length === 0 || candidates.length === 0) && (
            <span style={{ fontSize: '0.8rem', color: 'var(--status-degraded)', marginLeft: '1rem' }}>
              Ensure at least one job and one candidate exist.
            </span>
          )}
        </form>
      </div>

      {/* Applications List */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Submitted Applications ({applications.length})</h3>
          <button onClick={fetchData} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
            Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading applications...</div>
        ) : applications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No applications submitted yet.
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Application ID</th>
                  <th>Job ID</th>
                  <th>Candidate ID</th>
                  <th>Status</th>
                  <th>Applied At</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--accent-sky)' }}>
                      {app.id.substring(0, 8)}...
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                      {app.job_id.substring(0, 8)}...
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                      {app.candidate_id.substring(0, 8)}...
                    </td>
                    <td>
                      <span className="status-pill healthy" style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>
                        {app.status}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      {new Date(app.applied_at).toLocaleDateString()}
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
