'use client';

import React from 'react';
import Link from 'next/link';
import { Cpu, Terminal, ExternalLink, LogOut, LogIn, UserCheck, Shield } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export const Header: React.FC = () => {
  const { user, profile, role, logout } = useAuth();

  const getRoleBadgeStyle = (r: string | null) => {
    switch (r) {
      case 'ADMIN':
        return {
          background: 'rgba(239, 68, 68, 0.15)',
          color: '#f87171',
          border: '1px solid rgba(239, 68, 68, 0.3)',
        };
      case 'RECRUITER':
        return {
          background: 'rgba(139, 92, 246, 0.15)',
          color: '#a78bfa',
          border: '1px solid rgba(139, 92, 246, 0.3)',
        };
      case 'CANDIDATE':
        return {
          background: 'rgba(16, 185, 129, 0.15)',
          color: '#34d399',
          border: '1px solid rgba(16, 185, 129, 0.3)',
        };
      default:
        return {
          background: 'rgba(255, 255, 255, 0.1)',
          color: 'var(--text-muted)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        };
    }
  };

  return (
    <header className="navbar">
      <div className="logo-group">
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
          <div className="logo-icon">
            <Cpu size={22} color="#ffffff" />
          </div>
          <span className="logo-text">TalentForge</span>
        </Link>
        <span className="badge-phase">Phase 3: Auth &amp; RBAC</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <a
          href="http://localhost:8000/api/v1/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-secondary"
          id="btn-nav-docs"
          style={{ padding: '0.45rem 0.9rem', fontSize: '0.85rem' }}
        >
          <Terminal size={15} />
          <span>FastAPI Docs</span>
          <ExternalLink size={13} style={{ opacity: 0.7 }} />
        </a>

        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.35rem 0.75rem',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                fontSize: '0.85rem',
              }}
            >
              <UserCheck size={15} color="var(--accent-sky)" />
              <span style={{ fontWeight: 500 }}>{profile?.name || user.email}</span>
              <span
                style={{
                  padding: '0.15rem 0.5rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  ...getRoleBadgeStyle(role),
                }}
              >
                {role || 'SYNCING...'}
              </span>
            </div>

            <button
              onClick={() => logout()}
              className="btn-secondary"
              id="btn-logout"
              style={{ padding: '0.45rem 0.8rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              title="Sign Out"
            >
              <LogOut size={14} />
              <span>Logout</span>
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Link
              href="/login"
              className="btn-secondary"
              id="btn-nav-login"
              style={{ padding: '0.45rem 0.85rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <LogIn size={14} />
              <span>Sign In</span>
            </Link>
            <Link
              href="/signup"
              className="btn-primary"
              id="btn-nav-signup"
              style={{ padding: '0.45rem 0.85rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
            >
              <Shield size={14} />
              <span>Sign Up</span>
            </Link>
          </div>
        )}
      </div>
    </header>
  );
};

