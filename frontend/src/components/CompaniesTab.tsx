'use client';

import React, { useState, useEffect } from 'react';
import { ApiService } from '@/services/api';
import { Company } from '@/types/models';
import { Building2, Plus, Loader2, AlertCircle } from 'lucide-react';

export const CompaniesTab: React.FC = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCompanies = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ApiService.getCompanies();
      setCompanies(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load companies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await ApiService.createCompany({ name: name.trim(), description: description.trim() || undefined });
      setName('');
      setDescription('');
      await fetchCompanies();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create company');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Create Company Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.25rem' }}>
          <Building2 size={20} color="var(--accent-sky)" />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Create New Company</h3>
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
              <label className="form-label" htmlFor="company-name">Company Name *</label>
              <input
                id="company-name"
                className="form-input"
                placeholder="e.g. Acme Technologies"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="company-desc">Description</label>
              <input
                id="company-desc"
                className="form-input"
                placeholder="e.g. Next-generation autonomous computing"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>
          <button type="submit" id="btn-create-company" className="btn-primary" disabled={submitting}>
            {submitting ? <Loader2 size={16} className="spin" /> : <Plus size={16} />}
            <span>{submitting ? 'Creating...' : 'Create Company'}</span>
          </button>
        </form>
      </div>

      {/* Companies List */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Registered Companies ({companies.length})</h3>
          <button onClick={fetchCompanies} className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
            Refresh
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading companies...</div>
        ) : companies.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No companies registered yet. Create your first company above.
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {companies.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--accent-sky)' }}>
                      {c.id.substring(0, 8)}...
                    </td>
                    <td style={{ fontWeight: 600 }}>{c.name}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{c.description || '—'}</td>
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
