"use client";
import React, { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api';

export default function CandidateInterviewPage({ params }: { params: { id: string } }) {
    const [interview, setInterview] = useState<any>(null);
    const [questions, setQuestions] = useState<any[]>([]);
    const [currentAnswer, setCurrentAnswer] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadInterview();
    }, [params.id]);

    const loadInterview = async () => {
        try {
            const res = await apiFetch(`/interviews/${params.id}`);
            if (res.error) throw new Error(res.error);
            setInterview(res);
            if (res.status === 'IN_PROGRESS' || res.status === 'COMPLETED') {
                const qRes = await apiFetch(`/interviews/${params.id}/questions`);
                setQuestions(qRes);
            }
        } catch (e: any) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const startInterview = async () => {
        try {
            const res = await apiFetch(`/interviews/${params.id}/start`, { method: 'POST' });
            if (res.error) throw new Error(res.error);
            loadInterview();
        } catch (e: any) {
            alert(e.message);
        }
    };

    const submitAnswer = async (questionId: string) => {
        try {
            const res = await apiFetch(`/interviews/${params.id}/answers?question_id=${questionId}`, { 
                method: 'POST',
                body: JSON.stringify({ answer_text: currentAnswer })
            });
            if (res.error) throw new Error(res.error);
            setCurrentAnswer('');
            loadInterview();
        } catch (e: any) {
            alert(e.message);
        }
    };

    const completeInterview = async () => {
        try {
            const res = await apiFetch(`/interviews/${params.id}/complete`, { method: 'POST' });
            if (res.error) throw new Error(res.error);
            loadInterview();
        } catch (e: any) {
            alert(e.message);
        }
    };

    if (loading) return <div className="p-8">Loading...</div>;
    if (!interview) return <div className="p-8">Interview not found.</div>;

    return (
        <div className="p-8 max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">Interview Portal</h1>
            
            {interview.status === 'CREATED' && (
                <div className="card p-6 text-center">
                    <h2 className="text-xl mb-4">Welcome to your AI Interview</h2>
                    <p className="mb-4">You will be asked several questions to evaluate your fit for the role.</p>
                    <button onClick={startInterview} className="btn btn-primary px-8 py-3">Start Interview</button>
                </div>
            )}

            {interview.status === 'IN_PROGRESS' && questions.length > 0 && (
                <div className="card p-6">
                    {interview.current_question_index < questions.length ? (
                        <>
                            <h2 className="text-xl font-bold mb-2">Question {interview.current_question_index + 1} of {questions.length}</h2>
                            <p className="mb-4 text-lg">{questions[interview.current_question_index].question}</p>
                            <textarea 
                                className="form-input mb-4" 
                                rows={6} 
                                value={currentAnswer} 
                                onChange={(e) => setCurrentAnswer(e.target.value)}
                                placeholder="Type your answer here..."
                            ></textarea>
                            <button 
                                onClick={() => submitAnswer(questions[interview.current_question_index].id)} 
                                className="btn btn-primary"
                                disabled={!currentAnswer.trim()}
                            >
                                Submit Answer
                            </button>
                        </>
                    ) : (
                        <div className="text-center">
                            <h2 className="text-xl mb-4">All questions completed!</h2>
                            <button onClick={completeInterview} className="btn btn-primary px-8 py-3">Complete Interview</button>
                        </div>
                    )}
                </div>
            )}

            {interview.status === 'COMPLETED' && (
                <div className="card p-6 text-center">
                    <h2 className="text-xl text-green-500 font-bold mb-2">Interview Completed</h2>
                    <p>Thank you for your time. Your answers have been recorded.</p>
                </div>
            )}
        </div>
    );
}
