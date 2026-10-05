'use client';

import React, { useEffect, useState } from 'react';
import { ApiService } from '@/services/api';
import { UserProfile, UserRole } from '@/types/models';
import { Shield, UserCog, Check, RefreshCw, AlertCircle } from 'lucide-react';

export const AdminUsersTab: React.FC = () => {
  const [users, setUsers] = useState<UserProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await ApiService.getUsers();
      setUsers(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch users';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId: string, newRole: UserRole) => {
    setUpdatingId(userId);
    setMessage(null);
    setError(null);
    try {
      const updated = await ApiService.updateUserRole(userId, newRole);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
      setMessage(`Successfully updated role for ${updated.email} to ${newRole}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Role update failed';
      setError(msg);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: '0 0 0.25rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <UserCog size={20} color="var(--accent-indigo)" />
            <span>Admin RBAC &amp; User Role Management</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            Promote or manage system roles across registered platform users.
          </p>
        </div>

        <button
          onClick={fetchUsers}
          className="btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}
        >
          <RefreshCw size={14} className={loading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {message && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#34d399', fontSize: '0.85rem' }}>
          {message}
        </div>
      )}

      {error && (
        <div style={{ padding: '0.75rem 1rem', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#f87171', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>Name</th>
              <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>Email</th>
              <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600 }}>Current Role</th>
              <th style={{ padding: '0.85rem 1.25rem', fontWeight: 600, textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Loading registered users...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={4} style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No users found in database.
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                  <td style={{ padding: '0.85rem 1.25rem', fontWeight: 500 }}>{u.name}</td>
                  <td style={{ padding: '0.85rem 1.25rem', color: 'var(--text-muted)' }}>{u.email}</td>
                  <td style={{ padding: '0.85rem 1.25rem' }}>
                    <span
                      style={{
                        padding: '0.2rem 0.55rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        background:
                          u.role === 'ADMIN'
                            ? 'rgba(239, 68, 68, 0.15)'
                            : u.role === 'RECRUITER'
                            ? 'rgba(139, 92, 246, 0.15)'
                            : 'rgba(16, 185, 129, 0.15)',
                        color:
                          u.role === 'ADMIN'
                            ? '#f87171'
                            : u.role === 'RECRUITER'
                            ? '#a78bfa'
                            : '#34d399',
                      }}
                    >
                      {u.role}
                    </span>
                  </td>
                  <td style={{ padding: '0.85rem 1.25rem', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                      {u.role !== 'RECRUITER' && (
                        <button
                          disabled={updatingId === u.id}
                          onClick={() => handleRoleChange(u.id, 'RECRUITER')}
                          className="btn-secondary"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        >
                          Make Recruiter
                        </button>
                      )}
                      {u.role !== 'ADMIN' && (
                        <button
                          disabled={updatingId === u.id}
                          onClick={() => handleRoleChange(u.id, 'ADMIN')}
                          className="btn-secondary"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', color: '#f87171' }}
                        >
                          Make Admin
                        </button>
                      )}
                      {u.role !== 'CANDIDATE' && (
                        <button
                          disabled={updatingId === u.id}
                          onClick={() => handleRoleChange(u.id, 'CANDIDATE')}
                          className="btn-secondary"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                        >
                          Demote to Candidate
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
