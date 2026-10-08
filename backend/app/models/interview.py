import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text, Uuid, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.candidate import Candidate
    from app.models.job import Job

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False) # CREATED, IN_PROGRESS, COMPLETED, CANCELLED
    current_question_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    questions: Mapped[list["InterviewQuestion"]] = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    evaluations: Mapped[list["InterviewEvaluation"]] = relationship("InterviewEvaluation", back_populates="session", cascade="all, delete-orphan")

    application: Mapped["Application"] = relationship("Application")
    candidate: Mapped["Candidate"] = relationship("Candidate")
    job: Mapped["Job"] = relationship("Job")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    interview_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    competency: Mapped[str] = mapped_column(String(255), nullable=False)
    evaluation_criteria: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    session: Mapped["InterviewSession"] = relationship("InterviewSession", back_populates="questions")
    answers: Mapped[list["InterviewAnswer"]] = relationship("InterviewAnswer", back_populates="question", cascade="all, delete-orphan")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    interview_question_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    interview_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    question: Mapped["InterviewQuestion"] = relationship("InterviewQuestion", back_populates="answers")

class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    interview_session_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=True)
    evaluator_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. 'TECHNICAL', 'PROBLEM_SOLVING', 'FINAL'
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    strengths: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    structured_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    session: Mapped["InterviewSession"] = relationship("InterviewSession", back_populates="evaluations")
