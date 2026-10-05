'use client';

import React from 'react';
import { Cpu, Terminal, ExternalLink } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="navbar">
      <div className="logo-group">
        <div className="logo-icon">
          <Cpu size={22} color="#ffffff" />
        </div>
        <span className="logo-text">TalentForge</span>
        <span className="badge-phase">Phase 2: Database &amp; Storage</span>
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
      </div>
    </header>
  );
};
