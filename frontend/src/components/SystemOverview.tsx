'use client';

import React from 'react';
import { Layers, Box, Check, ShieldCheck, Terminal, Cpu, Database } from 'lucide-react';

export const SystemOverview: React.FC = () => {
  const stackItems = [
    {
      title: 'Frontend (App Router)',
      tech: 'Next.js 14 + TypeScript',
      desc: 'Modular App Router with client/server components, API service layer, and dark glassmorphic UI.',
      icon: <Box size={20} color="var(--accent-sky)" />,
    },
    {
      title: 'Backend API Gateway',
      tech: 'Python 3.12+ & FastAPI',
      desc: 'Asynchronous REST API with CORS, structured logging, global error foundation, and versioned routing.',
      icon: <Cpu size={20} color="var(--accent-cyan)" />,
    },
    {
      title: 'Data & ORM Layer',
      tech: 'SQLAlchemy 2.x + Alembic',
      desc: 'Declarative base, pooled session management, pre-ping health probes, and migration framework.',
      icon: <Database size={20} color="var(--accent-purple)" />,
    },
    {
      title: 'Containerization',
      tech: 'Docker & Docker Compose',
      desc: 'Multi-service configuration orchestrating frontend, backend, and postgres services with isolated networking.',
      icon: <Layers size={20} color="var(--status-healthy)" />,
    },
  ];

  const foundationPrinciples = [
    'Strict separation of concerns between frontend and backend',
    'Type-safe contracts with TypeScript and Pydantic v2',
    'Zero hardcoded credentials: configuration driven by environment variables',
    'Comprehensive automated health telemetry across API and DB layers',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Architecture Cards Grid */}
      <div>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-secondary)' }}>
          Phase 1: Architecture &amp; Core Infrastructure
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
          {stackItems.map((item, index) => (
            <div key={index} className="glass-card" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div style={{ padding: '0.5rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
                  {item.icon}
                </div>
                <div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>{item.title}</h4>
                  <span style={{ fontSize: '0.8rem', color: 'var(--accent-sky)' }}>{item.tech}</span>
                </div>
              </div>
              <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Compliance / Boundary Checklist */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <ShieldCheck size={20} color="var(--status-healthy)" />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Production Foundation Principles</h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem' }}>
          {foundationPrinciples.map((principle, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <div style={{ width: 18, height: 18, borderRadius: '50%', background: 'var(--status-healthy-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Check size={12} color="var(--status-healthy)" />
              </div>
              <span>{principle}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
