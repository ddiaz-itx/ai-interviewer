"""Message Classification Agent - classifies candidate messages."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.base import BaseAgent
from app.agents.llm_factory import get_llm
from app.agents.prompts import MESSAGE_CLASSIFICATION_PROMPT
from app.schemas.interview import MessageClassification
from app.agents.validators import MessageClassificationInput


class MessageClassificationAgent(BaseAgent):
    """Agent for classifying candidate messages."""

    def __init__(self):
        """Initialize the message classification agent."""
        super().__init__(agent_name="message_classification")
        self.llm = get_llm(temperature=0.0)  # Deterministic for consistency
        self.parser = PydanticOutputParser(pydantic_object=MessageClassification)

    async def classify(
        self,
        current_question: str,
        candidate_message: str,
        db: Optional[AsyncSession] = None,
        interview_id: Optional[int] = None,
    ) -> MessageClassification:
        """
        Classify a candidate's message.

        Args:
            current_question: The current question being asked
            candidate_message: The candidate's message to classify
            db: Database session for cost tracking
            interview_id: Interview ID for cost tracking

        Returns:
            MessageClassification with type and confidence
        """
        # Validate inputs
        self.validate_inputs(current_question=current_question, candidate_message=candidate_message)
        MessageClassificationInput(current_question=current_question, candidate_message=candidate_message)

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are analyzing interview messages."),
                (
                    "human",
                    MESSAGE_CLASSIFICATION_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your classification:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        inputs = {
            "current_question": current_question,
            "candidate_message": candidate_message,
            "format_instructions": self.parser.get_format_instructions(),
        }

        # Execute classification
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
async def classify_message(
    current_question: str,
    candidate_message: str,
    db: Optional[AsyncSession] = None,
    interview_id: Optional[int] = None,
) -> MessageClassification:
    """
    Classify a candidate's message.

    Args:
        current_question: Current question
        candidate_message: Message to classify
        db: Database session
        interview_id: Interview ID

    Returns:
        MessageClassification object
    """
    agent = MessageClassificationAgent()
    return await agent.classify(current_question, candidate_message, db, interview_id)
