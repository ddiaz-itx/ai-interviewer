"""Pydantic schemas for messages."""
from datetime import datetime

from pydantic import BaseModel, Field


# Telemetry
class Telemetry(BaseModel):
    """Telemetry data for a message."""

    response_time_ms: int | None = Field(None, description="Response time in milliseconds")
    paste_detected: bool = Field(default=False, description="Whether paste was detected")


# Answer Evaluation
class AnswerEvaluation(BaseModel):
    """Answer evaluation result from answer evaluation agent."""

    score: int = Field(..., ge=1, le=10, description="Quality score from 1-10")
    rationale: str = Field(..., description="Why this score was given")
    evidence: str = Field(..., description="Quote from answer supporting the score")
    followup_hint: str | None = Field(None, description="Idea for the next question")


# Message CRUD schemas
class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    role: str = Field(..., description="'assistant' or 'candidate'")
    content: str = Field(..., min_length=1)
    question_number: int | None = None
    difficulty_level: float | None = None
    answer_quality_score: int | None = Field(None, ge=1, le=10)
    cheat_certainty: float | None = Field(None, ge=0, le=100)
    telemetry: Telemetry | None = None


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: int
    interview_id: int
    role: str
    content: str
    timestamp: datetime
    question_number: int | None = None
    difficulty_level: float | None = None
    answer_quality_score: int | None = None
    cheat_certainty: float | None = None
    telemetry: dict | None = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class CandidateMessageSubmit(BaseModel):
    """Schema for candidate submitting a message."""

    content: str = Field(..., min_length=1)
    telemetry: Telemetry
