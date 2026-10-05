import React from 'react';
import { HealthStatusCard } from '@/components/HealthStatusCard';
import { SystemOverview } from '@/components/SystemOverview';
import { Sparkles, Terminal, ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3rem' }}>
      {/* Hero Header */}
      <section className="hero">
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.35rem 0.85rem', borderRadius: '9999px', background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.25)', marginBottom: '1.25rem', fontSize: '0.85rem', color: 'var(--accent-sky)' }}>
          <Sparkles size={14} />
          <span>Next-Generation Intelligent Talent Engine</span>
        </div>
        
        <h1 className="hero-title">
          TalentForge <span className="gradient-text">Project Foundation</span>
        </h1>
        
        <p className="hero-subtitle">
          Phase 1 setup established: Modular Next.js frontend, FastAPI asynchronous backend gateway,
          SQLAlchemy 2.x ORM with Alembic migrations, and automated telemetry health checks.
        </p>
      </section>

      {/* Real-time Health Telemetry */}
      <section id="section-health">
        <HealthStatusCard />
      </section>

      {/* Architecture & Foundation Spec */}
      <section id="section-architecture">
        <SystemOverview />
      </section>
    </div>
  );
}
