'use client';

import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div>
          <span>TalentForge &copy; {new Date().getFullYear()} &mdash; AI-Powered Hiring Platform Foundation</span>
        </div>
        <div style={{ display: 'flex', gap: '1.5rem' }}>
          <span>Next.js App Router (TypeScript)</span>
          <span>&bull;</span>
          <span>FastAPI (Python)</span>
          <span>&bull;</span>
          <span>SQLAlchemy 2.x + Alembic</span>
          <span>&bull;</span>
          <span>PostgreSQL</span>
        </div>
      </div>
    </footer>
  );
};
