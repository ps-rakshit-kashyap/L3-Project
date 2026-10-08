import uuid
from datetime import UTC, datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewEvaluation
from app.models.application import Application
from app.models.resume import Resume
from app.models.user import User, UserRole
from app.services.rag_service import rag_service
from app.services.resume_extractor import resume_extractor
from app.services.interview.question_generator import generate_questions
from app.services.interview.answer_evaluator import evaluate_answer
from app.services.interview.final_evaluator import evaluate_final

class InterviewService:
    def create_interview(self, db: Session, application_id: uuid.UUID) -> InterviewSession:
        app = db.query(Application).filter(Application.id == application_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Check if interview already exists
        existing = db.query(InterviewSession).filter(InterviewSession.application_id == application_id).first()
        if existing:
            return existing

        candidate = app.candidate
        if not candidate.resumes:
            raise HTTPException(status_code=400, detail="Candidate has no resume")
        resume = sorted(candidate.resumes, key=lambda r: r.uploaded_at)[-1]
        resume_text = resume_extractor.get_or_extract_text(db, resume)

        job_context = f"Title: {app.job.title}\nDescription: {app.job.description}\nRequirements: {app.job.requirements}"
        
        # RAG context for rubric
        rag_chunks = rag_service.search(db, query=f"{app.job.title} evaluation rubric", top_k=3)
        rubric_context = "\n".join(c.content for c in rag_chunks) if rag_chunks else "Standard evaluation rubric."

        session = InterviewSession(
            application_id=app.id,
            candidate_id=candidate.id,
            job_id=app.job.id,
            status="CREATED"
        )
        db.add(session)
        db.flush()

        questions_data = generate_questions(resume_text, job_context, rubric_context)
        for qd in questions_data:
            q = InterviewQuestion(
                interview_session_id=session.id,
                question=qd.question,
                category=qd.category,
                difficulty=qd.difficulty,
                competency=qd.competency,
                evaluation_criteria=qd.evaluation_criteria,
                order_index=qd.order_index
            )
            db.add(q)
        
        db.commit()
        db.refresh(session)
        return session

    def start_interview(self, db: Session, interview_id: uuid.UUID) -> InterviewSession:
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Interview not found")
        if session.status != "CREATED":
            return session
        
        session.status = "IN_PROGRESS"
        session.started_at = datetime.now(UTC)
        db.commit()
        db.refresh(session)
        return session

    def submit_answer(self, db: Session, interview_id: uuid.UUID, question_id: uuid.UUID, answer_text: str) -> InterviewAnswer:
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if not session or session.status != "IN_PROGRESS":
            raise HTTPException(status_code=400, detail="Interview not active")

        q = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id, InterviewQuestion.interview_session_id == interview_id).first()
        if not q:
            raise HTTPException(status_code=404, detail="Question not found")

        # Upsert answer
        ans = db.query(InterviewAnswer).filter(InterviewAnswer.interview_question_id == question_id).first()
        if not ans:
            ans = InterviewAnswer(interview_question_id=question_id, interview_session_id=interview_id, answer_text=answer_text)
            db.add(ans)
        else:
            ans.answer_text = answer_text
            ans.updated_at = datetime.now(UTC)
        
        session.current_question_index = q.order_index + 1
        db.flush()

        # Evaluate answer in background or sync (sync for POC)
        app = session.application
        candidate = app.candidate
        resume = sorted(candidate.resumes, key=lambda r: r.uploaded_at)[-1]
        resume_text = resume_extractor.get_or_extract_text(db, resume)
        job_context = f"Title: {app.job.title}\nDescription: {app.job.description}\nRequirements: {app.job.requirements}"
        
        eval_res = evaluate_answer(q.question, answer_text, resume_text, job_context, "Standard rubric", q.category)
        
        evaluation = db.query(InterviewEvaluation).filter(InterviewEvaluation.question_id == question_id).first()
        if not evaluation:
            evaluation = InterviewEvaluation(
                interview_session_id=interview_id,
                question_id=question_id,
                evaluator_type=q.category,
            )
            db.add(evaluation)
            
        evaluation.score = eval_res.score
        evaluation.strengths = eval_res.strengths
        evaluation.weaknesses = eval_res.weaknesses
        evaluation.evidence = eval_res.evidence
        evaluation.rationale = eval_res.rationale
        
        db.commit()
        db.refresh(ans)
        return ans

    def complete_interview(self, db: Session, interview_id: uuid.UUID) -> InterviewSession:
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Interview not found")
        if session.status == "COMPLETED":
            return session
            
        session.status = "COMPLETED"
        session.completed_at = datetime.now(UTC)
        
        # Final Evaluation
        evals = [{"evaluator_type": e.evaluator_type, "score": e.score} for e in session.evaluations if e.question_id]
        if evals:
            final_res = evaluate_final(evals)
            fin_eval = InterviewEvaluation(
                interview_session_id=interview_id,
                evaluator_type="FINAL",
                score=final_res.overall_score,
                strengths=final_res.strengths,
                weaknesses=final_res.weaknesses,
                evidence=final_res.evidence,
                rationale=final_res.summary,
                structured_result=final_res.model_dump()
            )
            db.add(fin_eval)

        db.commit()
        db.refresh(session)
        return session

interview_service = InterviewService()
