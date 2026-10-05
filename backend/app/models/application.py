import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.candidate import Candidate
    from app.models.evaluation import FinalEvaluation, InterviewResult, ScreeningResult
    from app.models.job import Job


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), default="applied", nullable=False, index=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    job: Mapped["Job"] = relationship("Job", back_populates="applications")
    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="applications")

    screening_results: Mapped[list["ScreeningResult"]] = relationship(
        "ScreeningResult", back_populates="application", cascade="all, delete-orphan"
    )
    interview_results: Mapped[list["InterviewResult"]] = relationship(
        "InterviewResult", back_populates="application", cascade="all, delete-orphan"
    )
    final_evaluations: Mapped[list["FinalEvaluation"]] = relationship(
        "FinalEvaluation", back_populates="application", cascade="all, delete-orphan"
    )
