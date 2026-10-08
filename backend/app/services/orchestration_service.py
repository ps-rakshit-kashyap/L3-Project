import uuid
import concurrent.futures
from datetime import UTC, datetime
from typing import Any, List, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.orchestration import OrchestrationRun, AgentExecution
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewEvaluation
from app.services.interview.question_generator import generate_questions
from app.services.interview.evaluators import evaluate_technical, evaluate_problem_solving, evaluate_communication, evaluate_role_fit
from app.services.interview.final_evaluator import evaluate_final
from app.services.resume_extractor import resume_extractor
from app.services.rag_service import rag_service
from langfuse import observe

class OrchestrationService:
    def _create_run(self, db: Session, interview_id: uuid.UUID, workflow_type: str) -> OrchestrationRun:
        run = OrchestrationRun(interview_session_id=interview_id, status="RUNNING", workflow_type=workflow_type)
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    def _mark_run_complete(self, db: Session, run: OrchestrationRun, status: str = "COMPLETED", error: str | None = None):
        run.status = status
        run.completed_at = datetime.now(UTC)
        run.error_message = error
        db.commit()
        db.refresh(run)

    def _create_execution(self, db: Session, run_id: uuid.UUID, agent_name: str, task: str, payload: dict) -> AgentExecution:
        execution = AgentExecution(
            run_id=run_id,
            agent_name=agent_name,
            task=task,
            status="PENDING",
            input_payload=payload
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def _mark_execution_complete(self, db: Session, execution: AgentExecution, status: str, result: dict | None = None, error: str | None = None):
        execution.status = status
        execution.completed_at = datetime.now(UTC)
        execution.result_payload = result
        execution.error_message = error
        db.commit()
        db.refresh(execution)

    @observe()
    def generate_questions_workflow(self, db: Session, interview_id: uuid.UUID) -> OrchestrationRun:
        run = self._create_run(db, interview_id, "GENERATE_QUESTIONS")
        
        try:
            session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
            if not session:
                raise ValueError("Interview not found")

            app = session.application
            candidate = app.candidate
            resume = sorted(candidate.resumes, key=lambda r: r.uploaded_at)[-1]
            resume_text = resume_extractor.get_or_extract_text(db, resume)
            job_context = f"Title: {app.job.title}\nDescription: {app.job.description}\nRequirements: {app.job.requirements}"
            
            rag_chunks = rag_service.search(db, query=f"{app.job.title} evaluation rubric", top_k=3)
            rubric_context = "\n".join(c.content for c in rag_chunks) if rag_chunks else "Standard evaluation rubric."

            # Agent Execution
            payload = {"candidate_context": resume_text, "job_context": job_context, "rubric_context": rubric_context}
            execution = self._create_execution(db, run.id, "QuestionGenerator", "Generate technical questions", payload)

            try:
                questions_data = generate_questions(resume_text, job_context, rubric_context)
                self._mark_execution_complete(db, execution, "SUCCESS", {"count": len(questions_data)})
                
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

            except Exception as e:
                self._mark_execution_complete(db, execution, "FAILED", error=str(e))
                raise

            self._mark_run_complete(db, run, "COMPLETED")
        except Exception as e:
            self._mark_run_complete(db, run, "FAILED", error=str(e))
            raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")
        
        return run

    @observe()
    def evaluate_answer_workflow(self, db: Session, interview_id: uuid.UUID, question_id: uuid.UUID, answer_text: str) -> OrchestrationRun:
        run = self._create_run(db, interview_id, "EVALUATE_ANSWER")
        try:
            session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
            q = db.query(InterviewQuestion).filter(InterviewQuestion.id == question_id, InterviewQuestion.interview_session_id == interview_id).first()
            
            app = session.application
            candidate = app.candidate
            resume = sorted(candidate.resumes, key=lambda r: r.uploaded_at)[-1]
            resume_text = resume_extractor.get_or_extract_text(db, resume)
            job_context = f"Title: {app.job.title}\nDescription: {app.job.description}\nRequirements: {app.job.requirements}"
            
            # Agents config
            agents = [
                ("TechnicalEvaluator", evaluate_technical, "TECHNICAL"),
                ("ProblemSolvingEvaluator", evaluate_problem_solving, "PROBLEM_SOLVING"),
                ("CommunicationEvaluator", evaluate_communication, "COMMUNICATION"),
                ("RoleFitEvaluator", evaluate_role_fit, "ROLE_FIT"),
            ]
            
            executions = []
            for agent_name, _, cat in agents:
                ex = self._create_execution(db, run.id, agent_name, f"Evaluate {cat}", {"question": q.question, "answer": answer_text})
                executions.append(ex)

            # Parallel execution
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = {}
                for idx, (agent_name, func, cat) in enumerate(agents):
                    futures[executor.submit(func, q.question, answer_text, resume_text, job_context, "Standard rubric")] = executions[idx]

                for future in concurrent.futures.as_completed(futures):
                    ex = futures[future]
                    try:
                        res = future.result()
                        # Save to db
                        evaluation = InterviewEvaluation(
                            interview_session_id=interview_id,
                            question_id=question_id,
                            evaluator_type=res.evaluator_type,
                            score=res.score,
                            strengths=res.strengths,
                            weaknesses=res.weaknesses,
                            evidence=res.evidence,
                            rationale=res.rationale
                        )
                        db.add(evaluation)
                        results.append(evaluation)
                        # We don't commit yet, to avoid race conditions. Will commit after.
                        self._mark_execution_complete(db, ex, "SUCCESS", {"score": res.score})
                    except Exception as e:
                        self._mark_execution_complete(db, ex, "FAILED", error=str(e))
                        
            db.commit()
            self._mark_run_complete(db, run, "COMPLETED")
        except Exception as e:
            self._mark_run_complete(db, run, "FAILED", error=str(e))
            raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")

        return run

    @observe()
    def complete_interview_workflow(self, db: Session, interview_id: uuid.UUID) -> OrchestrationRun:
        run = self._create_run(db, interview_id, "COMPLETE_INTERVIEW")
        try:
            session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
            
            evals = [{"evaluator_type": e.evaluator_type, "score": e.score} for e in session.evaluations if e.question_id]
            
            execution = self._create_execution(db, run.id, "FinalEvaluator", "Final Interview Score", {"evaluations": evals})
            try:
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
                self._mark_execution_complete(db, execution, "SUCCESS", {"score": final_res.overall_score})
            except Exception as e:
                self._mark_execution_complete(db, execution, "FAILED", error=str(e))
                raise

            self._mark_run_complete(db, run, "COMPLETED")
        except Exception as e:
            self._mark_run_complete(db, run, "FAILED", error=str(e))
            raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")
            
        return run

orchestration_service = OrchestrationService()
