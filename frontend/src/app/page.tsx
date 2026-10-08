'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { HealthStatusCard } from '@/components/HealthStatusCard';
import { SystemOverview } from '@/components/SystemOverview';
import { CompaniesTab } from '@/components/CompaniesTab';
import { JobsTab } from '@/components/JobsTab';
import { CandidatesTab } from '@/components/CandidatesTab';
import { ApplicationsTab } from '@/components/ApplicationsTab';
import { CandidatePortalTab } from '@/components/CandidatePortalTab';
import { AdminUsersTab } from '@/components/AdminUsersTab';
import { ScreeningDashboardTab } from '@/components/ScreeningDashboardTab';
import { KnowledgeTab } from '@/components/KnowledgeTab';
import { InterviewsTab } from '@/components/InterviewsTab';
import { useAuth } from '@/context/AuthContext';
import {
  Activity,
  Building2,
  Briefcase,
  Users,
  Send,
  Shield,
  UserCheck,
  UserCog,
  LogIn,
  Lock,
  Sparkles,
  BookOpen,
} from 'lucide-react';

type TabType =
  | 'telemetry'
  | 'candidate-portal'
  | 'companies'
  | 'jobs'
  | 'candidates'
  | 'applications'
  | 'screening'
  | 'interviews'
  | 'knowledge'
  | 'admin-users';

export default function HomePage() {
  const { user, profile, role, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('telemetry');

  // Automatically switch tab based on user role when authenticated
  useEffect(() => {
    if (role === 'CANDIDATE') {
      setActiveTab('candidate-portal');
    } else if (role === 'ADMIN' || role === 'RECRUITER') {
      setActiveTab('screening');
    }
  }, [role]);

  const canAccessRecruiter = role === 'ADMIN' || role === 'RECRUITER';
  const canAccessAdmin = role === 'ADMIN';

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
          <Sparkles size={14} color="var(--accent-purple)" />
          <span>Phase 4: AI Resume Screening Agent &amp; Scorecard</span>
        </div>

        <h1 className="hero-title">
          TalentForge <span className="gradient-text">AI Screening</span>
        </h1>

        <p className="hero-subtitle">
          Intelligent candidate resume parsing (PDF, DOCX, TXT), requirements evaluation,
          and structured AI scorecards empowering recruiters with objective hiring insights.
        </p>

        {/* Unauthenticated Alert Banner */}
        {!loading && !user && (
          <div
            style={{
              marginTop: '1.25rem',
              padding: '1rem 1.5rem',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '1rem',
              fontSize: '0.9rem',
            }}
          >
            <span style={{ color: 'var(--text-muted)' }}>
              Sign in to test role-based access for Candidates, Recruiters, and Admins:
            </span>
            <div style={{ display: 'flex', gap: '0.6rem' }}>
              <Link href="/login" className="btn-secondary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
                <LogIn size={13} style={{ marginRight: '0.3rem' }} />
                <span>Log In</span>
              </Link>
              <Link href="/signup" className="btn-primary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
                <span>Create Account</span>
              </Link>
            </div>
          </div>
        )}
      </section>

      {/* Role-Aware Navigation Tabs */}
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div className="nav-tabs" style={{ flexWrap: 'wrap', justifyContent: 'center' }}>
          {/* Candidate-specific Tab */}
          {role === 'CANDIDATE' && (
            <button
              id="tab-candidate-portal"
              className={`nav-tab-item ${activeTab === 'candidate-portal' ? 'active' : ''}`}
              onClick={() => setActiveTab('candidate-portal')}
            >
              <UserCheck size={16} />
              <span>My Candidate Portal</span>
            </button>
          )}

          {/* Admin User Management Tab */}
          {canAccessAdmin && (
            <button
              id="tab-admin-users"
              className={`nav-tab-item ${activeTab === 'admin-users' ? 'active' : ''}`}
              onClick={() => setActiveTab('admin-users')}
            >
              <UserCog size={16} />
              <span>User Roles (Admin)</span>
            </button>
          )}

          {/* Recruiter / Admin Tabs */}
          {canAccessRecruiter && (
            <button
              id="tab-companies"
              className={`nav-tab-item ${activeTab === 'companies' ? 'active' : ''}`}
              onClick={() => setActiveTab('companies')}
            >
              <Building2 size={16} />
              <span>Companies</span>
            </button>
          )}

          {/* Jobs Tab (All authenticated users can browse) */}
          <button
            id="tab-jobs"
            className={`nav-tab-item ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
          >
            <Briefcase size={16} />
            <span>Jobs</span>
          </button>

          {canAccessRecruiter && (
            <button
              id="tab-candidates"
              className={`nav-tab-item ${activeTab === 'candidates' ? 'active' : ''}`}
              onClick={() => setActiveTab('candidates')}
            >
              <Users size={16} />
              <span>All Candidates &amp; Resumes</span>
            </button>
          )}

          {canAccessRecruiter && (
            <button
              id="tab-applications"
              className={`nav-tab-item ${activeTab === 'applications' ? 'active' : ''}`}
              onClick={() => setActiveTab('applications')}
            >
              <Send size={16} />
              <span>Applications</span>
            </button>
          )}

          {canAccessRecruiter && (
            <button
              id="tab-screening"
              className={`nav-tab-item ${activeTab === 'screening' ? 'active' : ''}`}
              onClick={() => setActiveTab('screening')}
              style={{
                background: activeTab === 'screening' ? undefined : 'rgba(99, 102, 241, 0.08)',
                borderColor: activeTab === 'screening' ? undefined : 'rgba(99, 102, 241, 0.3)',
              }}
            >
              <Sparkles size={16} color="var(--accent-purple)" />
              <span style={{ fontWeight: 600 }}>AI Screening</span>
            </button>
          )}

          {canAccessRecruiter && (
            <button
              id="tab-knowledge"
              className={`nav-tab-item ${activeTab === 'knowledge' ? 'active' : ''}`}
              onClick={() => setActiveTab('knowledge')}
            >
              <BookOpen size={16} />
              <span>Knowledge Base</span>
            </button>
          )}

          {canAccessRecruiter && (
            <button
              id="tab-interviews"
              className={`nav-tab-item ${activeTab === 'interviews' ? 'active' : ''}`}
              onClick={() => setActiveTab('interviews')}
            >
              <Users size={16} />
              <span>Interviews</span>
            </button>
          )}

          {/* Health & Telemetry is always available */}
          <button
            id="tab-telemetry"
            className={`nav-tab-item ${activeTab === 'telemetry' ? 'active' : ''}`}
            onClick={() => setActiveTab('telemetry')}
          >
            <Activity size={16} />
            <span>Health &amp; Telemetry</span>
          </button>
        </div>
      </div>

      {/* Tab Panels */}
      <section id="tab-content" style={{ minHeight: '400px' }}>
        {activeTab === 'candidate-portal' && <CandidatePortalTab />}
        {activeTab === 'admin-users' && <AdminUsersTab />}
        {activeTab === 'companies' && (
          canAccessRecruiter ? (
            <CompaniesTab />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <Lock size={32} color="#f87171" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Access Restricted</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                Company management is restricted to Recruiter and Admin roles. Your current role is <strong>{role || 'Unauthenticated'}</strong>.
              </p>
            </div>
          )
        )}
        {activeTab === 'jobs' && <JobsTab />}
        {activeTab === 'candidates' && (
          canAccessRecruiter ? (
            <CandidatesTab />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <Lock size={32} color="#f87171" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Access Restricted</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                Listing all candidates and resumes requires a Recruiter or Admin role.
              </p>
            </div>
          )
        )}
        {activeTab === 'applications' && (
          canAccessRecruiter ? (
            <ApplicationsTab />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <Lock size={32} color="#f87171" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Access Restricted</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                Recruiter access required to view cross-candidate application data.
              </p>
            </div>
          )
        )}
        {activeTab === 'screening' && (
          canAccessRecruiter ? (
            <ScreeningDashboardTab />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <Lock size={32} color="#f87171" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Access Restricted</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                The AI Screening Dashboard is restricted to Recruiter and Admin roles.
              </p>
            </div>
          )
        )}
        {activeTab === 'knowledge' && (
          canAccessRecruiter ? (
            <KnowledgeTab />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <Lock size={32} color="#f87171" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Access Restricted</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                The Knowledge Base is restricted to Recruiter and Admin roles.
              </p>
            </div>
          )
        )}
        {activeTab === 'interviews' && (
          canAccessRecruiter ? (
            <InterviewsTab />
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
              <Lock size={32} color="#f87171" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Access Restricted</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto' }}>
                Interviews are restricted to Recruiter and Admin roles.
              </p>
            </div>
          )
        )}
        {activeTab === 'telemetry' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <HealthStatusCard />
            <SystemOverview />
          </div>
        )}
      </section>
    </div>
  );
}
