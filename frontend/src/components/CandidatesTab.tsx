'use client';

import React, { useState, useEffect } from 'react';
import { ApiService } from '@/services/api';
import { Candidate } from '@/types/models';
import { Users, Plus, Upload, FileText, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

export const CandidatesTab: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [summary, setSummary] = useState('');

  // Resume upload state
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCandidates = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ApiService.getCandidates();
      setCandidates(data);
      if (data.length > 0 && !selectedCandidateId) {
        setSelectedCandidateId(data[0].id);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load candidates');
    } finally {
      setLoading(false);
    }
  }, [selectedCandidateId]);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  const handleCreateCandidate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await ApiService.createCandidate({
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
        location: location.trim() || undefined,
        profile_summary: summary.trim() || undefined,
      });
      setName('');
      setEmail('');
      setPhone('');
      setLocation('');
      setSummary('');
      await fetchCandidates();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create candidate');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUploadResume = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCandidateId || !file) return;
    setUploading(true);
    setError(null);
    setUploadSuccess(null);
    try {
      const res = await ApiService.uploadResume(selectedCandidateId, file);
      setUploadSuccess(`Resume '${res.file_name}' uploaded successfully to Supabase Storage!`);
      setFile(null);
      // Reset input element value
      const fileInput = document.getElementById('resume-file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      await fetchCandidates();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Resume upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Create Candidate Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
          <Users size={20} color="var(--accent-sky)" />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Register New Candidate</h3>
        </div>

        {error && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--status-error-bg)', color: 'var(--status-error)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleCreateCandidate}>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="cand-name">Candidate Name *</label>
              <input
                id="cand-name"
                className="form-input"
                placeholder="e.g. Alex Morgan"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="cand-email">Email Address *</label>
              <input
                id="cand-email"
                type="email"
                className="form-input"
                placeholder="e.g. alex@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="cand-phone">Phone</label>
              <input
                id="cand-phone"
                className="form-input"
                placeholder="e.g. +1 555-0192"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="cand-location">Location</label>
              <input
                id="cand-location"
                className="form-input"
                placeholder="e.g. New York, NY"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="cand-summary">Profile Summary</label>
            <textarea
              id="cand-summary"
              className="form-textarea"
              placeholder="Brief summary of candidate experience and focus areas..."
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
            />
          </div>

          <button type="submit" id="btn-create-candidate" className="btn-primary" disabled={submitting}>
            {submitting ? <Loader2 size={16} className="spin" /> : <Plus size={16} />}
            <span>{submitting ? 'Registering...' : 'Register Candidate'}</span>
          </button>
        </form>
      </div>

      {/* Upload Candidate Resume Card */}
      <div className="glass-card" style={{ border: '1px solid rgba(99, 102, 241, 0.25)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
          <Upload size={20} color="var(--accent-cyan)" />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Upload Candidate Resume (Supabase Storage)</h3>
        </div>

        {uploadSuccess && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--status-healthy-bg)', color: 'var(--status-healthy)', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.85rem' }}>
            <CheckCircle2 size={16} />
            <span>{uploadSuccess}</span>
          </div>
        )}

        <form onSubmit={handleUploadResume}>
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="select-candidate-resume">Select Candidate *</label>
              <select
                id="select-candidate-resume"
                className="form-select"
                value={selectedCandidateId}
                onChange={(e) => setSelectedCandidateId(e.target.value)}
                required
              >
                <option value="">-- Choose Candidate --</option>
                {candidates.map((cand) => (
                  <option key={cand.id} value={cand.id}>
                    {cand.name} ({cand.email})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="resume-file-input">Resume File (PDF, DOCX, TXT - max 10MB) *</label>
              <input
                id="resume-file-input"
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                className="form-input"
                onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                required
              />
            </div>
          </div>

          <button
            type="submit"
            id="btn-upload-resume"
            className="btn-primary"
            disabled={uploading || !file || !selectedCandidateId}
          >
            {uploading ? <Loader2 size={16} className="spin" /> : <Upload size={16} />}
            <span>{uploading ? 'Uploading to Supabase Storage...' : 'Upload Resume Document'}</span>
          </button>
        </form>
      </div>

      {/* Candidate List */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Candidate Directory ({candidates.length})</h3>
          <button onClick={fetchCandidates} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
            Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading candidates...</div>
        ) : candidates.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No candidates registered yet.
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Location</th>
                  <th>Resumes Attached</th>
                  <th>Registered</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontWeight: 600 }}>{c.name}</td>
                    <td style={{ color: 'var(--accent-sky)' }}>{c.email}</td>
                    <td>{c.location || '—'}</td>
                    <td>
                      {c.resumes && c.resumes.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                          {c.resumes.map((r) => (
                            <span key={r.id} style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', color: 'var(--status-healthy)' }}>
                              <FileText size={13} />
                              {r.file_name}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>None</span>
                      )}
                    </td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      {new Date(c.created_at).toLocaleDateString()}
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
