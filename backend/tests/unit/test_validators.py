import pytest
from pydantic import ValidationError
from app.agents.validators import (
    DocumentInput,
    QuestionAnswerInput,
    QuestionGenerationInput,
    MessageClassificationInput,
)

class TestValidators:
    """Test suite for Pydantic validators."""

    def test_document_input_validation(self):
        """Test DocumentInput validation."""
        # Valid input
        valid_input = {
            "resume_text": "A" * 50,
            "role_description_text": "B" * 20,
            "job_offering_text": "C" * 20,
        }
        model = DocumentInput(**valid_input)
        assert model.resume_text == "A" * 50

        # Invalid: Empty string (whitespace)
        with pytest.raises(ValidationError) as exc:
            DocumentInput(
                resume_text=" " * 51,
                role_description_text="B" * 20,
                job_offering_text="C" * 20
            )
        assert "Text cannot be empty" in str(exc.value)

        # Invalid: Too short
        with pytest.raises(ValidationError) as exc:
            DocumentInput(
                resume_text="Short",
                role_description_text="B" * 20,
                job_offering_text="C" * 20
            )
        assert "String should have at least 50 characters" in str(exc.value)

    def test_question_answer_input_validation(self):
        """Test QuestionAnswerInput validation."""
        # Valid input
        valid_input = {
            "question": "What is Python?",  # > 10 chars
            "answer": "A programming language."
        }
        model = QuestionAnswerInput(**valid_input)
        assert model.question == "What is Python?"

        # Invalid: Question too short
        with pytest.raises(ValidationError):
            QuestionAnswerInput(question="Short", answer="Valid answer")

        # Invalid: Answer empty
        with pytest.raises(ValidationError) as exc:
            QuestionAnswerInput(question="What is Python?", answer="   ")
        assert "Text cannot be empty" in str(exc.value)

    def test_question_generation_input_validation(self):
        """Test QuestionGenerationInput validation."""
        # Valid input
        valid_input = {
            "focus_areas": ["Python", "API"],
            "difficulty_level": 5.0,
            "questions_asked": 2
        }
        model = QuestionGenerationInput(**valid_input)
        assert model.focus_areas == ["Python", "API"]

        # Invalid: Empty list item
        with pytest.raises(ValidationError) as exc:
            QuestionGenerationInput(
                focus_areas=["Python", "   "],
                difficulty_level=5.0,
                questions_asked=2
            )
        assert "Focus areas cannot be empty" in str(exc.value)

        # Invalid: Difficulty out of range
        with pytest.raises(ValidationError):
            QuestionGenerationInput(
                focus_areas=["Python"],
                difficulty_level=11.0,
                questions_asked=2
            )

    def test_message_classification_input_validation(self):
        """Test MessageClassificationInput validation."""
        # Valid input
        valid_input = {
            "current_question": "What is validation?",
            "candidate_message": "Checking correctness."
        }
        model = MessageClassificationInput(**valid_input)
        assert model.current_question == "What is validation?"

        # Invalid: Empty message
        with pytest.raises(ValidationError) as exc:
            MessageClassificationInput(
                current_question="What is validation?",
                candidate_message="   "
            )
        assert "Text cannot be empty" in str(exc.value)
