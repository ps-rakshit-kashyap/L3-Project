'use client';

import React, { useEffect, useState, useRef } from 'react';
import { ApiService } from '@/services/api';
import { Candidate, Resume, Job, Application } from '@/types/models';
import { useAuth } from '@/context/AuthContext';
import { User, FileText, Briefcase, Send, Upload, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export const CandidatePortalTab: React.FC = () => {
  const { user, profile } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [creatingProfile, setCreatingProfile] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [applyingJobId, setApplyingJobId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Profile creation state
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [summary, setSummary] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Load candidate profile
      let cand: Candidate | null = null;
      try {
        cand = await ApiService.getMyCandidateProfile();
        setCandidate(cand);
      } catch {
        setCandidate(null);
      }

      // 2. Load open jobs
      try {
        const jobList = await ApiService.getJobs();
        setJobs(jobList.filter((j) => j.status === 'open'));
      } catch (err: unknown) {
        console.warn('Jobs load error:', err);
      }

      // 3. Load my applications
      try {
        const appList = await ApiService.getApplications();
        setApplications(appList);
      } catch (err: unknown) {
        console.warn('Applications load error:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const handleCreateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile?.email) return;

    setCreatingProfile(true);
    setError(null);
    setMessage(null);

    try {
      const newCand = await ApiService.createCandidate({
        name: profile.name,
        email: profile.email,
        phone: phone || undefined,
        location: location || undefined,
        profile_summary: summary || undefined,
      });
      setCandidate(newCand);
      setMessage('Candidate profile created successfully!');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create profile';
      setError(msg);
    } finally {
      setCreatingProfile(false);
    }
  };

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !candidate) return;

    setUploadingResume(true);
    setError(null);
    setMessage(null);

    try {
      const res = await ApiService.uploadResume(candidate.id, file);
      setMessage(`Resume '${res.file_name}' uploaded successfully to Supabase Storage!`);
      // Reload profile to reflect resume
      const updatedCand = await ApiService.getMyCandidateProfile();
      setCandidate(updatedCand);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Resume upload failed';
      setError(msg);
    } finally {
      setUploadingResume(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleApply = async (jobId: string) => {
    if (!candidate) {
      setError('Please create your candidate profile first before applying.');
      return;
    }

    setApplyingJobId(jobId);
    setError(null);
    setMessage(null);

    try {
      await ApiService.createApplication({
        job_id: jobId,
        candidate_id: candidate.id,
      });
      setMessage('Application submitted successfully!');
      const updatedApps = await ApiService.getApplications();
      setApplications(updatedApps);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Application submission failed';
      setError(msg);
    } finally {
      setApplyingJobId(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.3rem', fontWeight: 600, margin: '0 0 0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <User size={20} color="var(--accent-emerald)" />
            <span>Candidate Portal</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            Manage your personal hiring profile, uploaded resumes, and active job applications.
          </p>
        </div>

        <button onClick={loadData} className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {message && (
        <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34d399', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CheckCircle2 size={16} />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div style={{ padding: '0.85rem 1rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#f87171', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Profile & Resume Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Profile Card */}
        <div className="card">
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <User size={18} color="var(--accent-sky)" />
            <span>My Profile</span>
          </h3>

          {candidate ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Name: </span>
                <span style={{ fontWeight: 600 }}>{candidate.name}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Email: </span>
                <span>{candidate.email}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Phone: </span>
                <span>{candidate.phone || 'Not provided'}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Location: </span>
                <span>{candidate.location || 'Not provided'}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>Summary: </span>
                <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-main)' }}>
                  {candidate.profile_summary || 'No summary entered.'}
                </p>
              </div>
            </div>
          ) : (
            <form onSubmit={handleCreateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                You do not have a candidate profile linked to <strong>{profile?.email}</strong> yet. Create one below:
              </p>
              <div>
                <input
                  type="text"
                  placeholder="Phone (optional)"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="input-field"
                  style={{ width: '100%', fontSize: '0.85rem' }}
                />
              </div>
              <div>
                <input
                  type="text"
                  placeholder="Location (e.g. San Francisco, CA)"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="input-field"
                  style={{ width: '100%', fontSize: '0.85rem' }}
                />
              </div>
              <div>
                <textarea
                  placeholder="Profile Summary (experience, skills, target roles)"
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  className="input-field"
                  rows={3}
                  style={{ width: '100%', fontSize: '0.85rem', resize: 'vertical' }}
                />
              </div>
              <button
                type="submit"
                disabled={creatingProfile}
                className="btn-primary"
                style={{ fontSize: '0.85rem' }}
              >
                {creatingProfile ? 'Creating Profile...' : 'Save Candidate Profile'}
              </button>
            </form>
          )}
        </div>

        {/* Resumes Card */}
        <div className="card">
          <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={18} color="var(--accent-purple)" />
            <span>My Resumes</span>
          </h3>

          {candidate ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={handleResumeUpload}
                  style={{ display: 'none' }}
                  id="resume-file-input"
                />
                <button
                  type="button"
                  disabled={uploadingResume}
                  onClick={() => fileInputRef.current?.click()}
                  className="btn-secondary"
                  style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '0.5rem', fontSize: '0.85rem' }}
                >
                  <Upload size={16} />
                  <span>{uploadingResume ? 'Uploading...' : 'Upload New Resume (PDF, DOCX)'}</span>
                </button>
              </div>

              {candidate.resumes && candidate.resumes.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {candidate.resumes.map((r) => (
                    <div
                      key={r.id}
                      style={{
                        padding: '0.65rem 0.85rem',
                        borderRadius: '6px',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid rgba(255, 255, 255, 0.08)',
                        fontSize: '0.8rem',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <FileText size={15} color="var(--accent-sky)" />
                        <span style={{ fontWeight: 500 }}>{r.file_name}</span>
                      </div>
                      {r.file_url && (
                        <a
                          href={r.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: 'var(--accent-sky)', textDecoration: 'none', fontSize: '0.75rem' }}
                        >
                          View File
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
                  No resume uploaded yet.
                </p>
              )}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
              Create your profile first to enable resume upload.
            </p>
          )}
        </div>
      </div>

      {/* Applications Section */}
      <div className="card">
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Send size={18} color="var(--accent-emerald)" />
          <span>My Applications ({applications.length})</span>
        </h3>

        {applications.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            You haven&apos;t applied for any jobs yet. Browse open jobs below and apply!
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
            {applications.map((app) => (
              <div
                key={app.id}
                style={{
                  padding: '0.85rem 1.25rem',
                  borderRadius: '8px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.2rem' }}>
                    Job ID: {app.job_id}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    Applied: {new Date(app.applied_at).toLocaleDateString()}
                  </div>
                </div>
                <span
                  style={{
                    padding: '0.2rem 0.6rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background: 'rgba(99, 102, 241, 0.15)',
                    color: 'var(--accent-sky)',
                  }}
                >
                  {app.status.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Browse Open Jobs */}
      <div className="card">
        <h3 style={{ fontSize: '1.05rem', fontWeight: 600, margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Briefcase size={18} color="var(--accent-sky)" />
          <span>Browse Available Jobs</span>
        </h3>

        {jobs.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            No open jobs available currently. Check back soon.
          </p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
            {jobs.map((j) => {
              const alreadyApplied = applications.some((a) => a.job_id === j.id);
              return (
                <div
                  key={j.id}
                  style={{
                    padding: '1rem',
                    borderRadius: '8px',
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid rgba(255, 255, 255, 0.06)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '0.75rem',
                  }}
                >
                  <div>
                    <h4 style={{ margin: '0 0 0.35rem 0', fontSize: '0.95rem', fontWeight: 600 }}>{j.title}</h4>
                    <p style={{ margin: '0 0 0.5rem 0', color: 'var(--text-muted)', fontSize: '0.8rem', lineHeight: 1.4 }}>
                      {j.description}
                    </p>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <span>{j.employment_type}</span>
                      <span>•</span>
                      <span>{j.location || 'Remote'}</span>
                    </div>
                  </div>

                  <button
                    disabled={alreadyApplied || applyingJobId === j.id || !candidate}
                    onClick={() => handleApply(j.id)}
                    className="btn-primary"
                    style={{
                      padding: '0.4rem 0.8rem',
                      fontSize: '0.8rem',
                      width: '100%',
                      opacity: alreadyApplied ? 0.6 : 1,
                    }}
                  >
                    {alreadyApplied
                      ? 'Already Applied'
                      : applyingJobId === j.id
                      ? 'Applying...'
                      : candidate
                      ? 'Apply Now'
                      : 'Create Profile to Apply'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
