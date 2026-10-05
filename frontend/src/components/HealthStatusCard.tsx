'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { ApiService } from '@/services/api';
import { HealthStatusResponse } from '@/types/health';
import { Activity, Server, Database, RefreshCw, AlertCircle, CheckCircle2, ShieldAlert } from 'lucide-react';

export const HealthStatusCard: React.FC = () => {
  const [health, setHealth] = useState<HealthStatusResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [lastChecked, setLastChecked] = useState<Date | null>(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    try {
      const data = await ApiService.getHealth();
      setHealth(data);
      setLastChecked(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    // Auto-refresh every 15 seconds
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  const getStatusClass = (status?: string) => {
    if (!status) return 'degraded';
    if (status === 'healthy' || status === 'available' || status === 'connected') return 'healthy';
    if (status === 'degraded') return 'degraded';
    return 'disconnected';
  };

  return (
    <div className="glass-card" id="health-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Activity size={22} color="var(--accent-sky)" />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>System Health &amp; Telemetry</h2>
        </div>
        <button
          id="btn-refresh-health"
          onClick={fetchHealth}
          disabled={loading}
          className="btn-primary"
          style={{ padding: '0.45rem 0.9rem', fontSize: '0.85rem' }}
          title="Refresh health status"
        >
          <RefreshCw size={15} className={loading ? 'spin' : ''} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          <span>{loading ? 'Checking...' : 'Refresh'}</span>
        </button>
      </div>

      {/* Main Status Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
        {/* Overall Status */}
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Overall Status</span>
            <div className={`indicator-dot ${getStatusClass(health?.status)}`} />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              id="status-overall"
              className={`status-pill ${getStatusClass(health?.status)}`}
            >
              {health?.status || 'Loading...'}
            </span>
          </div>
        </div>

        {/* Backend API */}
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>FastAPI Gateway</span>
            <Server size={16} color="var(--accent-cyan)" />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              id="status-api"
              className={`status-pill ${getStatusClass(health?.api)}`}
            >
              {health?.api === 'available' ? 'Available (200 OK)' : health?.api || 'Checking...'}
            </span>
          </div>
        </div>

        {/* PostgreSQL Database */}
        <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>PostgreSQL Engine</span>
            <Database size={16} color="var(--accent-purple)" />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span
              id="status-database"
              className={`status-pill ${getStatusClass(health?.database)}`}
            >
              {health?.database === 'connected' ? 'Connected (SQLAlchemy 2.x)' : health?.database || 'Checking...'}
            </span>
          </div>
        </div>
      </div>

      {/* Meta Information Bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', background: 'rgba(0, 0, 0, 0.25)', padding: '0.9rem 1.25rem', borderRadius: '10px', fontSize: '0.825rem', color: 'var(--text-muted)' }}>
        <div>
          <strong style={{ color: 'var(--text-secondary)' }}>Target Endpoint:</strong>{' '}
          <code style={{ color: 'var(--accent-sky)' }}>GET /api/v1/health</code>
        </div>
        <div>
          <strong style={{ color: 'var(--text-secondary)' }}>Environment:</strong>{' '}
          <span style={{ color: 'var(--text-primary)' }}>{health?.environment || 'unknown'}</span>
        </div>
        <div>
          <strong style={{ color: 'var(--text-secondary)' }}>API Version:</strong>{' '}
          <span style={{ color: 'var(--text-primary)' }}>{health?.version || 'unknown'}</span>
        </div>
        <div>
          <strong style={{ color: 'var(--text-secondary)' }}>Last Checked:</strong>{' '}
          <span>{lastChecked ? lastChecked.toLocaleTimeString() : 'Pending...'}</span>
        </div>
      </div>

      {/* Connection Notice / Error Display if degraded or disconnected */}
      {health && health.database_error && (
        <div style={{ background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.25)', borderRadius: '10px', padding: '1rem', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
          <AlertCircle size={20} color="var(--status-degraded)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ fontSize: '0.85rem' }}>
            <div style={{ fontWeight: 600, color: 'var(--status-degraded)', marginBottom: '0.25rem' }}>
              Database Connectivity Advisory
            </div>
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              The API server is running, but the database probe reported:
              <pre style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'rgba(0, 0, 0, 0.4)', borderRadius: '6px', fontSize: '0.775rem', overflowX: 'auto', whiteSpace: 'pre-wrap', color: '#fca5a5' }}>
                {health.database_error}
              </pre>
              Ensure PostgreSQL is running and update <code>DATABASE_URL</code> in your <code>.env</code> file.
            </div>
          </div>
        </div>
      )}

      {health && health.status === 'healthy' && (
        <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '10px', padding: '0.85rem 1rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <CheckCircle2 size={18} color="var(--status-healthy)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--status-healthy)' }}>
            All foundation services are operational! FastAPI and PostgreSQL connection checks passed.
          </span>
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
