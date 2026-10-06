'use client';

import React, { useState, useEffect, useTransition } from 'react';
import { ApiService } from '@/services/api';
import { Application, Job, Candidate, ScreeningResult, ScreeningEvaluation } from '@/types/models';
import {
  Sparkles,
  CheckCircle,
  XCircle,
  AlertTriangle,
  HelpCircle,
  RefreshCw,
  Search,
  BookOpen,
  Briefcase,
  GraduationCap,
  MessageSquare,
  Award,
  ChevronRight,
  X,
  FileText,
} from 'lucide-react';

export const ScreeningDashboardTab: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [screenings, setScreenings] = useState<Record<string, ScreeningResult>>({});

  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [recommendationFilter, setRecommendationFilter] = useState<string>('ALL');

  const [loading, setLoading] = useState(false);
  const [screeningAppId, setScreeningAppId] = useState<string | null>(null);
  const [activeModalResult, setActiveModalResult] = useState<{
    result: ScreeningResult;
    candidateName: string;
    jobTitle: string;
  } | null>(null);

  const [customNotes, setCustomNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  const fetchData = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [appsData, jobsData, candidatesData, screeningsList] = await Promise.all([
        ApiService.getApplications(),
        ApiService.getJobs(),
        ApiService.getCandidates(),
        ApiService.getScreenings(),
      ]);

      setApplications(appsData);
      setJobs(jobsData);
      setCandidates(candidatesData);

      // Index screenings by application_id
      const map: Record<string, ScreeningResult> = {};
      screeningsList.forEach((s) => {
        map[s.application_id] = s;
      });
      setScreenings(map);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load screening dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRunScreening = async (appId: string, force: boolean = false) => {
    setScreeningAppId(appId);
    setError(null);
    try {
      const result = await ApiService.triggerScreening(appId, force, customNotes || undefined);
      startTransition(() => {
        setScreenings((prev) => ({ ...prev, [appId]: result }));
        setApplications((prev) =>
          prev.map((a) => (a.id === appId ? { ...a, status: 'screened' } : a))
        );
      });

      // Auto-open scorecard modal for immediate review
      const app = applications.find((a) => a.id === appId);
      const cand = candidates.find((c) => c.id === app?.candidate_id);
      const job = jobs.find((j) => j.id === app?.job_id);
      setActiveModalResult({
        result,
        candidateName: cand?.name || 'Applicant',
        jobTitle: job?.title || 'Target Role',
      });
      setCustomNotes('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'AI screening execution failed');
    } finally {
      setScreeningAppId(null);
    }
  };

  // Helper maps
  const candidateMap = new Map(candidates.map((c) => [c.id, c]));
  const jobMap = new Map(jobs.map((j) => [j.id, j]));

  // Filtering
  const filteredApps = applications.filter((app) => {
    if (selectedJobId && app.job_id !== selectedJobId) return false;
    if (recommendationFilter !== 'ALL') {
      const s = screenings[app.id];
      if (!s && recommendationFilter === 'PENDING') return true;
      if (!s) return false;
      if (s.recommendation !== recommendationFilter) return false;
    }
    return true;
  });

  // Analytics stats
  const totalScreened = Object.keys(screenings).length;
  const advanceCount = Object.values(screenings).filter((s) => s.recommendation === 'ADVANCE').length;
  const holdCount = Object.values(screenings).filter((s) => s.recommendation === 'HOLD').length;
  const rejectCount = Object.values(screenings).filter((s) => s.recommendation === 'REJECT').length;
  const avgScore =
    totalScreened > 0
      ? Math.round(
          Object.values(screenings).reduce((acc, curr) => acc + (curr.score || 0), 0) / totalScreened
        )
      : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Header / Stats Cards */}
      <div className="glass-card" style={{ padding: '1.5rem 1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Sparkles size={22} color="var(--accent-purple)" />
              <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0 }}>
                AI Resume Screening Agent
              </h2>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.25rem' }}>
              Autonomous candidate evaluation against role requirements, tech stack, and depth of experience.
            </p>
          </div>
          <button
            onClick={fetchData}
            className="btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}
          >
            <RefreshCw size={14} className={loading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Metric Badges */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.03)', border: '1px solid var(--border-light)', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>{totalScreened}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Screened</div>
          </div>
          <div style={{ background: 'rgba(52, 211, 153, 0.05)', border: '1px solid rgba(52, 211, 153, 0.2)', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--status-healthy)' }}>{advanceCount}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--status-healthy)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Advance</div>
          </div>
          <div style={{ background: 'rgba(251, 191, 36, 0.05)', border: '1px solid rgba(251, 191, 36, 0.2)', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--status-degraded)' }}>{holdCount}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--status-degraded)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Hold</div>
          </div>
          <div style={{ background: 'rgba(248, 113, 113, 0.05)', border: '1px solid rgba(248, 113, 113, 0.2)', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--status-error)' }}>{rejectCount}</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--status-error)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Reject</div>
          </div>
          <div style={{ background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.2)', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-purple)' }}>{avgScore}%</div>
            <div style={{ fontSize: '0.78rem', color: 'var(--accent-purple)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Avg Match</div>
          </div>
        </div>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--status-error-bg)', color: 'var(--status-error)', padding: '0.85rem 1.25rem', borderRadius: '8px', fontSize: '0.88rem' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="glass-card" style={{ padding: '1rem 1.25rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '220px' }}>
          <label htmlFor="filter-job" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Job:</label>
          <select
            id="filter-job"
            className="form-select"
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}
          >
            <option value="">All Job Openings ({jobs.length})</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>{j.title}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label htmlFor="filter-rec" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Recommendation:</label>
          <select
            id="filter-rec"
            className="form-select"
            value={recommendationFilter}
            onChange={(e) => setRecommendationFilter(e.target.value)}
            style={{ fontSize: '0.85rem', padding: '0.4rem 0.75rem' }}
          >
            <option value="ALL">All Outcomes</option>
            <option value="ADVANCE">Advance Only</option>
            <option value="HOLD">Hold Only</option>
            <option value="REJECT">Reject Only</option>
            <option value="PENDING">Pending Screening</option>
          </select>
        </div>
      </div>

      {/* Candidates & Applications Table */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Candidate Application Pipeline ({filteredApps.length})</h3>
        </div>

        {loading && applications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            Loading candidate applications...
          </div>
        ) : filteredApps.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No applications match the active filters.
          </div>
        ) : (
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Job Applied</th>
                  <th>Resume</th>
                  <th>Match Score</th>
                  <th>AI Recommendation</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredApps.map((app) => {
                  const cand = candidateMap.get(app.candidate_id);
                  const job = jobMap.get(app.job_id);
                  const screening = screenings[app.id];
                  const isScreeningThis = screeningAppId === app.id;

                  const hasResume = cand?.resumes && cand.resumes.length > 0;

                  return (
                    <tr key={app.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                          {cand?.name || 'Unknown Candidate'}
                        </div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {cand?.email}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 500 }}>{job?.title || 'Unknown Job'}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          {job?.employment_type || 'Full-time'}
                        </div>
                      </td>
                      <td>
                        {hasResume ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-sky)', fontSize: '0.8rem' }}>
                            <FileText size={14} />
                            <span>{cand?.resumes?.[0]?.file_name || 'Resume'}</span>
                          </div>
                        ) : (
                          <span style={{ fontSize: '0.78rem', color: 'var(--status-error)' }}>
                            No resume uploaded
                          </span>
                        )}
                      </td>
                      <td>
                        {screening ? (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div
                              style={{
                                width: '36px',
                                height: '36px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '0.85rem',
                                fontWeight: 700,
                                background:
                                  (screening.score || 0) >= 70
                                    ? 'rgba(52, 211, 153, 0.15)'
                                    : (screening.score || 0) >= 50
                                    ? 'rgba(251, 191, 36, 0.15)'
                                    : 'rgba(248, 113, 113, 0.15)',
                                color:
                                  (screening.score || 0) >= 70
                                    ? 'var(--status-healthy)'
                                    : (screening.score || 0) >= 50
                                    ? 'var(--status-degraded)'
                                    : 'var(--status-error)',
                                border: `1px solid ${
                                  (screening.score || 0) >= 70
                                    ? 'rgba(52, 211, 153, 0.4)'
                                    : (screening.score || 0) >= 50
                                    ? 'rgba(251, 191, 36, 0.4)'
                                    : 'rgba(248, 113, 113, 0.4)'
                                }`,
                              }}
                            >
                              {Math.round(screening.score || 0)}
                            </div>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ 100</span>
                          </div>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Not evaluated</span>
                        )}
                      </td>
                      <td>
                        {screening ? (
                          <span
                            className={`status-pill ${
                              screening.recommendation === 'ADVANCE'
                                ? 'healthy'
                                : screening.recommendation === 'HOLD'
                                ? 'degraded'
                                : 'down'
                            }`}
                            style={{ fontSize: '0.78rem', padding: '0.25rem 0.65rem', fontWeight: 600 }}
                          >
                            {screening.recommendation === 'ADVANCE' && <CheckCircle size={12} style={{ display: 'inline', marginRight: '4px' }} />}
                            {screening.recommendation === 'HOLD' && <AlertTriangle size={12} style={{ display: 'inline', marginRight: '4px' }} />}
                            {screening.recommendation === 'REJECT' && <XCircle size={12} style={{ display: 'inline', marginRight: '4px' }} />}
                            {screening.recommendation}
                          </span>
                        ) : (
                          <span className="status-pill degraded" style={{ fontSize: '0.78rem', opacity: 0.6 }}>
                            PENDING
                          </span>
                        )}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                          {screening ? (
                            <>
                              <button
                                onClick={() =>
                                  setActiveModalResult({
                                    result: screening,
                                    candidateName: cand?.name || 'Applicant',
                                    jobTitle: job?.title || 'Role',
                                  })
                                }
                                className="btn-secondary"
                                style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                              >
                                <BookOpen size={13} />
                                <span>Scorecard</span>
                              </button>
                              <button
                                onClick={() => handleRunScreening(app.id, true)}
                                disabled={isScreeningThis || !hasResume}
                                className="btn-secondary"
                                title="Re-screen with AI"
                                style={{ padding: '0.35rem 0.5rem', fontSize: '0.78rem' }}
                              >
                                <RefreshCw size={13} className={isScreeningThis ? 'spin' : ''} />
                              </button>
                            </>
                          ) : (
                            <button
                              onClick={() => handleRunScreening(app.id, false)}
                              disabled={isScreeningThis || !hasResume}
                              className="btn-primary"
                              style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                            >
                              <Sparkles size={13} className={isScreeningThis ? 'spin' : ''} />
                              <span>{isScreeningThis ? 'Evaluating...' : 'Screen with AI'}</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detailed Scorecard Modal */}
      {activeModalResult && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1.5rem',
          }}
          onClick={() => setActiveModalResult(null)}
        >
          <div
            style={{
              background: '#0d1322',
              border: '1px solid var(--border-light)',
              borderRadius: '16px',
              maxWidth: '850px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              padding: '2rem',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-light)', paddingBottom: '1.25rem' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                  <Award size={20} color="var(--accent-purple)" />
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    AI Screening Scorecard
                  </span>
                </div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, margin: 0 }}>
                  {activeModalResult.candidateName}
                </h2>
                <p style={{ color: 'var(--accent-sky)', fontSize: '0.9rem', margin: 0 }}>
                  for {activeModalResult.jobTitle}
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: (activeModalResult.result.score || 0) >= 70 ? 'var(--status-healthy)' : 'var(--status-degraded)' }}>
                    {Math.round(activeModalResult.result.score || 0)}%
                  </div>
                  <span
                    className={`status-pill ${
                      activeModalResult.result.recommendation === 'ADVANCE'
                        ? 'healthy'
                        : activeModalResult.result.recommendation === 'HOLD'
                        ? 'degraded'
                        : 'down'
                    }`}
                  >
                    {activeModalResult.result.recommendation}
                  </span>
                </div>

                <button
                  onClick={() => setActiveModalResult(null)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '0.5rem' }}
                >
                  <X size={20} />
                </button>
              </div>
            </div>

            {/* Scorecard Body */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Executive Summary */}
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem 1.25rem', borderRadius: '10px', borderLeft: '3px solid var(--accent-purple)' }}>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.4rem', letterSpacing: '0.5px' }}>
                  Executive Summary
                </h4>
                <p style={{ fontSize: '0.92rem', lineHeight: 1.5, margin: 0, color: 'var(--text-primary)' }}>
                  {activeModalResult.result.summary}
                </p>
              </div>

              {/* Strengths & Weaknesses */}
              {activeModalResult.result.details && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                  {/* Strengths */}
                  <div style={{ background: 'rgba(52, 211, 153, 0.04)', border: '1px solid rgba(52, 211, 153, 0.2)', padding: '1.25rem', borderRadius: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--status-healthy)', fontWeight: 600 }}>
                      <CheckCircle size={16} />
                      <span>Key Strengths</span>
                    </div>
                    <ul style={{ margin: 0, paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.86rem', color: 'var(--text-primary)' }}>
                      {(activeModalResult.result.details.strengths || []).map((s, idx) => (
                        <li key={idx}>{s}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Weaknesses / Gaps */}
                  <div style={{ background: 'rgba(248, 113, 113, 0.04)', border: '1px solid rgba(248, 113, 113, 0.2)', padding: '1.25rem', borderRadius: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--status-error)', fontWeight: 600 }}>
                      <AlertTriangle size={16} />
                      <span>Identified Gaps & Concerns</span>
                    </div>
                    <ul style={{ margin: 0, paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.86rem', color: 'var(--text-primary)' }}>
                      {(activeModalResult.result.details.weaknesses || []).map((w, idx) => (
                        <li key={idx}>{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Skills Matrix */}
              {activeModalResult.result.details?.skills_analysis && (
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Briefcase size={16} color="var(--accent-sky)" />
                    <span>Skills Match Matrix</span>
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.6rem' }}>
                    {activeModalResult.result.details.skills_analysis.map((sm, idx) => (
                      <div
                        key={idx}
                        style={{
                          background: sm.matched ? 'rgba(52, 211, 153, 0.05)' : 'rgba(255, 255, 255, 0.02)',
                          border: `1px solid ${sm.matched ? 'rgba(52, 211, 153, 0.25)' : 'var(--border-light)'}`,
                          borderRadius: '8px',
                          padding: '0.75rem 1rem',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                          <span style={{ fontWeight: 600, fontSize: '0.88rem' }}>{sm.skill}</span>
                          {sm.matched ? (
                            <span style={{ color: 'var(--status-healthy)', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '3px' }}>
                              <CheckCircle size={12} /> Matched
                            </span>
                          ) : (
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Missing</span>
                          )}
                        </div>
                        {sm.evidence && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.3 }}>
                            {sm.evidence}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Experience & Education */}
              {activeModalResult.result.details && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-sky)', marginBottom: '0.35rem' }}>
                      <Briefcase size={14} />
                      <span>Experience Evaluation</span>
                    </div>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-primary)', margin: 0, lineHeight: 1.4 }}>
                      {activeModalResult.result.details.experience_assessment}
                    </p>
                  </div>

                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-purple)', marginBottom: '0.35rem' }}>
                      <GraduationCap size={14} />
                      <span>Education Evaluation</span>
                    </div>
                    <p style={{ fontSize: '0.84rem', color: 'var(--text-primary)', margin: 0, lineHeight: 1.4 }}>
                      {activeModalResult.result.details.education_assessment}
                    </p>
                  </div>
                </div>
              )}

              {/* Recommended Interview Questions */}
              {activeModalResult.result.details?.recommended_interview_questions && (
                <div style={{ background: 'rgba(99, 102, 241, 0.04)', border: '1px solid rgba(99, 102, 241, 0.2)', padding: '1.25rem', borderRadius: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: 'var(--accent-purple)', fontWeight: 600 }}>
                    <MessageSquare size={16} />
                    <span>Recommended Interview Probe Questions</span>
                  </div>
                  <ol style={{ margin: 0, paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.86rem', color: 'var(--text-primary)' }}>
                    {activeModalResult.result.details.recommended_interview_questions.map((q, idx) => (
                      <li key={idx}>{q}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.75rem', gap: '0.75rem' }}>
              <button
                onClick={() => setActiveModalResult(null)}
                className="btn-secondary"
                style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
