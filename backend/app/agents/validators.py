"""Input validators for agents."""
from pydantic import BaseModel, Field, field_validator


class DocumentInput(BaseModel):
    """Validated input for document analysis."""

    resume_text: str = Field(..., min_length=50, max_length=20000)
    role_description_text: str = Field(..., min_length=20, max_length=10000)
    job_offering_text: str = Field(..., min_length=20, max_length=10000)

    @field_validator("resume_text", "role_description_text", "job_offering_text")
    @classmethod
    def not_empty_or_whitespace(cls, v: str) -> str:
        """Ensure text is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class QuestionAnswerInput(BaseModel):
    """Validated input for question/answer operations."""

    question: str = Field(..., min_length=10, max_length=1000)
    answer: str = Field(..., min_length=1, max_length=5000)

    @field_validator("question", "answer")
    @classmethod
    def not_empty_or_whitespace(cls, v: str) -> str:
        """Ensure text is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class QuestionGenerationInput(BaseModel):
    """Validated input for question generation."""

    focus_areas: list[str] = Field(..., min_length=1, max_length=10)
    difficulty_level: float = Field(..., ge=3.0, le=10.0)
    chat_history: str = Field(default="", max_length=50000)
    questions_asked: int = Field(..., ge=0, le=50)

    @field_validator("focus_areas")
    @classmethod
    def validate_focus_areas(cls, v: list[str]) -> list[str]:
        """Ensure focus areas are not empty."""
        if not all(area.strip() for area in v):
            raise ValueError("Focus areas cannot be empty")
        return [area.strip() for area in v]


class MessageClassificationInput(BaseModel):
    """Validated input for message classification."""

    current_question: str = Field(..., min_length=10, max_length=1000)
    candidate_message: str = Field(..., min_length=1, max_length=5000)

    @field_validator("current_question", "candidate_message")
    @classmethod
    def not_empty_or_whitespace(cls, v: str) -> str:
        """Ensure text is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class IntegrityAdjustmentInput(BaseModel):
    """Validated input for integrity assessment."""

    question: str = Field(..., min_length=10, max_length=1000)
    answer: str = Field(..., min_length=1, max_length=5000)
    response_time_ms: int = Field(..., ge=0)
    paste_detected: bool = Field(default=False)

    @field_validator("question", "answer")
    @classmethod
    def not_empty_or_whitespace(cls, v: str) -> str:
        """Ensure text is not empty or just whitespace."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()
