"use client";
import React, { useState } from 'react';
import { apiFetch } from '@/lib/api';

export const InterviewsTab: React.FC = () => {
    const [appId, setAppId] = useState('');
    const [interviewId, setInterviewId] = useState('');
    const [interview, setInterview] = useState<any>(null);

    const createInterview = async () => {
        try {
            const res = await apiFetch(`/interviews?application_id=${appId}`, { method: 'POST' });
            if (res.error) throw new Error(res.error);
            setInterview(res);
            setInterviewId(res.id);
            alert("Interview created!");
        } catch (e: any) {
            alert(e.message);
        }
    };

    const loadInterview = async () => {
        try {
            const res = await apiFetch(`/interviews/${interviewId}`);
            if (res.error) throw new Error(res.error);
            setInterview(res);
        } catch (e: any) {
            alert(e.message);
        }
    };

    return (
        <div className="tab-content fade-in">
            <h2 className="text-xl font-bold mb-4">Interviews Management</h2>
            <div style={{ display: 'flex', gap: '2rem' }}>
                <div style={{ flex: 1 }}>
                    <h3>Create Interview</h3>
                    <input 
                        type="text" 
                        placeholder="Application ID" 
                        value={appId} 
                        onChange={(e) => setAppId(e.target.value)} 
                        className="form-input mb-2"
                    />
                    <button onClick={createInterview} className="btn btn-primary">Create</button>
                </div>
                <div style={{ flex: 1 }}>
                    <h3>View Interview</h3>
                    <input 
                        type="text" 
                        placeholder="Interview ID" 
                        value={interviewId} 
                        onChange={(e) => setInterviewId(e.target.value)} 
                        className="form-input mb-2"
                    />
                    <button onClick={loadInterview} className="btn btn-primary">Load</button>
                </div>
            </div>

            {interview && (
                <div className="card mt-4 p-4">
                    <h3>Interview Details</h3>
                    <p>Status: {interview.status}</p>
                    <p>Candidate ID: {interview.candidate_id}</p>
                    
                    {interview.questions && (
                        <div>
                            <h4>Questions</h4>
                            <ul>
                                {interview.questions.map((q: any) => (
                                    <li key={q.id}>{q.category}: {q.question}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {interview.evaluations && interview.evaluations.length > 0 && (
                        <div className="mt-4">
                            <h4>Evaluations</h4>
                            {interview.evaluations.map((e: any) => (
                                <div key={e.id} className="p-2 border mb-2">
                                    <p><strong>{e.evaluator_type}</strong> - Score: {e.score}</p>
                                    <p>Rationale: {e.rationale}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
