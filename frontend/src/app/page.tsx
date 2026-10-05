'use client';

import React, { useState } from 'react';
import { HealthStatusCard } from '@/components/HealthStatusCard';
import { SystemOverview } from '@/components/SystemOverview';
import { CompaniesTab } from '@/components/CompaniesTab';
import { JobsTab } from '@/components/JobsTab';
import { CandidatesTab } from '@/components/CandidatesTab';
import { ApplicationsTab } from '@/components/ApplicationsTab';
import {
  Activity,
  Building2,
  Briefcase,
  Users,
  Send,
  Database,
  Sparkles,
} from 'lucide-react';

type TabType = 'telemetry' | 'companies' | 'jobs' | 'candidates' | 'applications';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<TabType>('telemetry');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
      {/* Hero Header */}
      <section className="hero">
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            background: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            marginBottom: '1rem',
            fontSize: '0.85rem',
            color: 'var(--accent-sky)',
          }}
        >
          <Database size={14} />
          <span>Phase 2: Database &amp; Storage Verification Console</span>
        </div>

        <h1 className="hero-title">
          TalentForge <span className="gradient-text">Data &amp; Storage</span>
        </h1>

        <p className="hero-subtitle">
          Supabase PostgreSQL, pgvector embedding foundation, SQLAlchemy 2.x ORM, Alembic migrations,
          and Supabase Storage resume management.
        </p>
      </section>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div className="nav-tabs">
          <button
            id="tab-telemetry"
            className={`nav-tab-item ${activeTab === 'telemetry' ? 'active' : ''}`}
            onClick={() => setActiveTab('telemetry')}
          >
            <Activity size={16} />
            <span>Health &amp; Telemetry</span>
          </button>
          <button
            id="tab-companies"
            className={`nav-tab-item ${activeTab === 'companies' ? 'active' : ''}`}
            onClick={() => setActiveTab('companies')}
          >
            <Building2 size={16} />
            <span>Companies</span>
          </button>
          <button
            id="tab-jobs"
            className={`nav-tab-item ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
          >
            <Briefcase size={16} />
            <span>Jobs</span>
          </button>
          <button
            id="tab-candidates"
            className={`nav-tab-item ${activeTab === 'candidates' ? 'active' : ''}`}
            onClick={() => setActiveTab('candidates')}
          >
            <Users size={16} />
            <span>Candidates &amp; Resumes</span>
          </button>
          <button
            id="tab-applications"
            className={`nav-tab-item ${activeTab === 'applications' ? 'active' : ''}`}
            onClick={() => setActiveTab('applications')}
          >
            <Send size={16} />
            <span>Applications</span>
          </button>
        </div>
      </div>

      {/* Tab Panels */}
      <section id="tab-content" style={{ minHeight: '400px' }}>
        {activeTab === 'telemetry' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <HealthStatusCard />
            <SystemOverview />
          </div>
        )}

        {activeTab === 'companies' && <CompaniesTab />}
        {activeTab === 'jobs' && <JobsTab />}
        {activeTab === 'candidates' && <CandidatesTab />}
        {activeTab === 'applications' && <ApplicationsTab />}
      </section>
    </div>
  );
}
