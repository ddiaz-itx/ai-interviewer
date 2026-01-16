"""Question Generation Agent - generates adaptive interview questions."""
from typing import Optional
from langchain.prompts import ChatPromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent
from app.agents.llm_factory import get_llm
from app.agents.prompts import QUESTION_GENERATION_PROMPT
from app.agents.validators import QuestionGenerationInput


class QuestionGenerationAgent(BaseAgent):
    """Agent for generating interview questions."""

    def __init__(self):
        """Initialize the question generation agent."""
        super().__init__(agent_name="question_generation")
        self.llm = get_llm(temperature=0.7)  # Some creativity for varied questions

    async def generate_question(
        self,
        focus_areas: list[str],
        difficulty_level: float,
        chat_history: str,
        questions_asked: int,
        db: Optional[AsyncSession] = None,
        interview_id: Optional[int] = None,
    ) -> str:
        """
        Generate the next interview question.

        Args:
            focus_areas: List of topics to cover in the interview
            difficulty_level: Current difficulty (3-10 scale)
            chat_history: Previous conversation context
            questions_asked: Number of questions already asked
            db: Database session for cost tracking
            interview_id: Interview ID for cost tracking

        Returns:
            The next question to ask
        """
        # Validate inputs
        self.validate_inputs(
            difficulty_level=difficulty_level,
            questions_asked=questions_asked
        )
        
        # Additional Pydantic validation
        QuestionGenerationInput(
            focus_areas=focus_areas,
            difficulty_level=difficulty_level,
            chat_history=chat_history or "",
            questions_asked=questions_asked
        )

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical interviewer."),
                ("human", QUESTION_GENERATION_PROMPT),
            ]
        )

        # Create the chain
        chain = prompt | self.llm

        inputs = {
            "focus_areas": ", ".join(focus_areas),
            "difficulty_level": difficulty_level,
            "chat_history": chat_history or "No previous questions yet.",
            "questions_asked": questions_asked,
        }

        # Execute question generation
        result = await self.invoke_with_retry_async(
            chain=chain,
            inputs=inputs,
            model=getattr(self.llm, "model_name", "unknown"),
            temperature=0.7,
            db=db,
            interview_id=interview_id,
        )

        # Extract the text content
        return result.content.strip()


# Convenience function
async def generate_question(
    focus_areas: list[str],
    difficulty_level: float,
    chat_history: str = "",
    questions_asked: int = 0,
    db: Optional[AsyncSession] = None,
    interview_id: Optional[int] = None,
) -> str:
    """
    Generate the next interview question.

    Args:
        focus_areas: Topics to cover
        difficulty_level: Current difficulty (3-10)
        chat_history: Previous conversation
        questions_asked: Number of questions asked
        db: Database session
        interview_id: Interview ID

    Returns:
        Next question string
    """
    agent = QuestionGenerationAgent()
    return await agent.generate_question(
        focus_areas, difficulty_level, chat_history, questions_asked, db, interview_id
    )
