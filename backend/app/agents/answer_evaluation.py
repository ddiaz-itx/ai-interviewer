"""Answer Evaluation Agent - scores and evaluates candidate answers."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.base import BaseAgent
from app.agents.llm_factory import get_llm
from app.agents.prompts import ANSWER_EVALUATION_PROMPT
from app.schemas.message import AnswerEvaluation
from app.agents.validators import QuestionAnswerInput


class AnswerEvaluationAgent(BaseAgent):
    """Agent for evaluating candidate answers."""

    def __init__(self):
        """Initialize the answer evaluation agent."""
        super().__init__(agent_name="answer_evaluation")
        self.llm = get_llm(temperature=0.0)  # Deterministic for fairness
        self.parser = PydanticOutputParser(pydantic_object=AnswerEvaluation)

    async def evaluate(
        self,
        question: str,
        answer: str,
        db: Optional[AsyncSession] = None,
        interview_id: Optional[int] = None,
    ) -> AnswerEvaluation:
        """
        Evaluate a candidate's answer to a question.

        Args:
            question: The question that was asked
            answer: The candidate's answer
            db: Database session for cost tracking
            interview_id: Interview ID for cost tracking

        Returns:
            AnswerEvaluation with score, rationale, evidence, and followup hint
        """
        # Validate inputs
        self.validate_inputs(question=question, answer=answer)
        QuestionAnswerInput(question=question, answer=answer)

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical interviewer."),
                (
                    "human",
                    ANSWER_EVALUATION_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your evaluation:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        inputs = {
            "question": question,
            "answer": answer,
            "format_instructions": self.parser.get_format_instructions(),
        }

        # Execute the evaluation
        result = await self.invoke_with_retry_async(
            chain=chain,
            inputs=inputs,
            model=getattr(self.llm, "model_name", "unknown"),
            temperature=0.0,
            db=db,
            interview_id=interview_id,
        )

        return result


# Convenience function
async def evaluate_answer(
    question: str,
    answer: str,
    db: Optional[AsyncSession] = None,
    interview_id: Optional[int] = None,
) -> AnswerEvaluation:
    """
    Evaluate a candidate's answer.

    Args:
        question: The question asked
        answer: The candidate's answer
        db: Database session
        interview_id: Interview ID

    Returns:
        AnswerEvaluation object
    """
    agent = AnswerEvaluationAgent()
    return await agent.evaluate(question, answer, db, interview_id)
