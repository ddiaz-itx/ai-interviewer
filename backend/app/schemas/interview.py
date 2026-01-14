"""Pydantic schemas for interviews."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


# Match Analysis schemas
class MatchAnalysis(BaseModel):
    """Match analysis result from document analysis agent."""

    match_score: int = Field(..., ge=1, le=10, description="Match score from 1-10")
    match_summary: str = Field(..., description="Explanation of the match score")
    focus_areas: list[str] = Field(..., description="Top 3-5 areas to probe in interview")


# Integrity schemas
class IntegrityFlag(BaseModel):
    """Integrity flag in final report."""

    message_reference: str = Field(..., description="Message ID or question number")
    question_number: int | None = Field(None, description="Question number if applicable")
    certainty_percentage: float = Field(..., ge=0, le=100, description="Certainty percentage")
    indicators: list[str] = Field(..., description="List of indicators")
    question_text: str = Field(..., description="The question that was asked")
    answer_excerpt: str = Field(..., description="Excerpt from the answer")


class IntegrityAssessment(BaseModel):
    """Per-message integrity assessment (optional)."""

    cheat_certainty: float = Field(..., ge=0, le=100, description="Cheat certainty percentage")
    indicators: list[str] = Field(..., description="List of indicators")


# Final Report schemas
class FinalReport(BaseModel):
    """Final interview report."""

    interview_score: int = Field(..., ge=1, le=10, description="Overall interview score")
    summary: str = Field(..., description="Performance summary")
    gaps: list[str] = Field(..., description="Areas needing improvement")
    meeting_expectations: list[str] = Field(..., description="Areas meeting expectations")
    integrity_flags: list[IntegrityFlag] = Field(
        default_factory=list, description="Integrity flags with details"
    )


# Message Classification
class MessageClassification(BaseModel):
    """Classification of candidate message."""

    type: str = Field(..., description="Answer, Clarification, or OffTopic")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence")


# Interview CRUD schemas
class InterviewCreate(BaseModel):
    """Schema for creating a new interview."""

    target_questions: int = Field(default=8, ge=1, le=20)
    difficulty_start: int = Field(default=5, ge=3, le=10)


class InterviewUpload(BaseModel):
    """Schema for document upload response."""

    resume_path: str
    role_path: str
    job_offering_path: str


class InterviewResponse(BaseModel):
    """Schema for interview response."""

    id: int
    status: str
    resume_path: str | None = None
    role_path: str | None = None
    job_offering_path: str | None = None
    match_analysis_json: dict[str, Any] | None = None
    target_questions: int
    difficulty_start: int
    candidate_link_token: str | None = None
    report_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterviewListResponse(BaseModel):
    """Schema for interview list item."""

    id: int
    status: str
    target_questions: int
    match_score: int | None = None
    interview_score: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
