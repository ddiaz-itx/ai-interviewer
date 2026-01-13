"""Message model."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.interview import Interview


class Message(Base):
    """Message entity representing a single message in the interview transcript."""

    __tablename__ = "messages"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key
    interview_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Message metadata
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'assistant' or 'candidate'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Question/Answer metadata (nullable for non-Q/A messages)
    question_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    answer_quality_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 1-10 scale

    # Integrity tracking (optional per message)
    cheat_certainty: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )  # 0-100 percentage

    # Telemetry (JSON: response_time_ms, paste_detected)
    telemetry: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview", back_populates="messages")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Message(id={self.id}, interview_id={self.interview_id}, role={self.role})>"
