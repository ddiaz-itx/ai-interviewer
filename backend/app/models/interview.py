"""Interview model."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.utils.state_machine import InterviewStatus

if TYPE_CHECKING:
    from app.models.message import Message


class Interview(Base):
    """Interview entity representing a candidate interview session."""

    __tablename__ = "interviews"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=InterviewStatus.DRAFT.value, index=True
    )

    # Document references
    resume_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    job_offering_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Match analysis (JSON)
    match_analysis_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Interview configuration
    target_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    difficulty_start: Mapped[int] = mapped_column(Integer, nullable=False, default=5)

    # Candidate access
    candidate_link_token: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, index=True
    )

    # Final report (JSON)
    report_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="interview", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Interview(id={self.id}, status={self.status})>"
