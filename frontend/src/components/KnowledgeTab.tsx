'use client';

import React, { useState, useEffect } from 'react';
import { ApiService } from '@/services/api';
import { BookOpen, Upload, Trash2, Search, Plus } from 'lucide-react';

interface KnowledgeDocument {
  id: string;
  title: string;
  source_type: string;
}

export const KnowledgeTab: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState('generic');
  const [textContent, setTextContent] = useState('');

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('tf_token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/knowledge`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const data = await res.json();
      setDocuments(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !textContent) return;
    
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('tf_token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/knowledge`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ title, text: textContent, source_type: sourceType })
      });
      if (!res.ok) throw new Error('Ingestion failed');
      
      setTitle('');
      setTextContent('');
      await fetchDocs();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      const token = localStorage.getItem('tf_token');
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/knowledge/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchDocs();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
          <BookOpen size={20} color="var(--accent-purple)" />
          Knowledge Base (RAG)
        </h2>
        
        {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

        <form onSubmit={handleIngest} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <input 
              type="text" 
              placeholder="Document Title" 
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="form-input"
              style={{ flex: 1 }}
            />
            <select 
              value={sourceType} 
              onChange={(e) => setSourceType(e.target.value)}
              className="form-select"
            >
              <option value="generic">Generic</option>
              <option value="policy">Policy</option>
              <option value="rubric">Evaluation Rubric</option>
            </select>
          </div>
          <textarea 
            placeholder="Paste document content here for RAG ingestion..."
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
            className="form-textarea"
            rows={5}
          />
          <button type="submit" disabled={loading} className="btn-primary" style={{ alignSelf: 'flex-start' }}>
            <Upload size={16} style={{ marginRight: '0.5rem' }}/>
            Ingest Document
          </button>
        </form>

        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr key={doc.id}>
                  <td>{doc.title}</td>
                  <td>{doc.source_type}</td>
                  <td>
                    <button onClick={() => handleDelete(doc.id)} className="btn-secondary" style={{ color: 'var(--status-error)' }}>
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))}
              {documents.length === 0 && (
                <tr><td colSpan={3} style={{ textAlign: 'center', padding: '2rem' }}>No knowledge documents found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
