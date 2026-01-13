"""Message service - business logic for message operations."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import (
    classify_message,
    evaluate_answer,
    generate_question,
    assess_integrity,
)
from app.models import Interview, Message
from app.schemas.message import CandidateMessageSubmit, MessageCreate
from app.utils.state_machine import InterviewStatus


class MessageService:
    """Service for message business logic."""

    @staticmethod
    async def get_messages(
        db: AsyncSession, interview_id: int
    ) -> list[Message]:
        """
        Get all messages for an interview.

        Args:
            db: Database session
            interview_id: Interview ID

        Returns:
            List of messages ordered by timestamp
        """
        result = await db.execute(
            select(Message)
            .where(Message.interview_id == interview_id)
            .order_by(Message.timestamp)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_message(
        db: AsyncSession, interview_id: int, message_data: MessageCreate
    ) -> Message:
        """
        Create a new message.

        Args:
            db: Database session
            interview_id: Interview ID
            message_data: Message data

        Returns:
            Created message
        """
        message = Message(
            interview_id=interview_id,
            role=message_data.role,
            content=message_data.content,
            question_number=message_data.question_number,
            difficulty_level=message_data.difficulty_level,
            answer_quality_score=message_data.answer_quality_score,
            cheat_certainty=message_data.cheat_certainty,
            telemetry=message_data.telemetry.model_dump() if message_data.telemetry else None,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    @staticmethod
    async def process_candidate_message(
        db: AsyncSession, interview_id: int, candidate_message: CandidateMessageSubmit
    ) -> dict:
        """
        Process candidate message and generate AI response.

        This is the main interview loop:
        1. Classify the message (Answer/Clarification/OffTopic)
        2. If Answer: Evaluate it and generate next question
        3. If Clarification: Provide clarification
        4. If OffTopic: Redirect to current question

        Args:
            db: Database session
            interview_id: Interview ID
            candidate_message: Candidate's message with telemetry

        Returns:
            Dict with assistant response and metadata

        Raises:
            ValueError: If interview not found or not in progress
        """
        # Get interview
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        if interview.status != InterviewStatus.IN_PROGRESS.value:
            raise ValueError("Interview is not in progress")

        # Get messages to find current question
        messages = await MessageService.get_messages(db, interview_id)

        # Find the last assistant question
        last_question = None
        question_number = 0
        for msg in reversed(messages):
            if msg.role == "assistant" and msg.question_number:
                last_question = msg.content
                question_number = msg.question_number
                break

        if not last_question:
            raise ValueError("No current question found")

        # Classify the message
        classification = classify_message(last_question, candidate_message.content)

        # Handle based on classification
        if classification.type == "Answer":
            # Evaluate the answer
            evaluation = evaluate_answer(last_question, candidate_message.content)

            # Optional: Assess integrity
            previous_answers = [
                msg.content for msg in messages
                if msg.role == "candidate"
            ]
            integrity = None
            if candidate_message.telemetry.paste_detected or candidate_message.telemetry.response_time_ms < 5000:
                integrity = assess_integrity(
                    last_question,
                    candidate_message.content,
                    candidate_message.telemetry.response_time_ms or 0,
                    candidate_message.telemetry.paste_detected,
                    previous_answers,
                )

            # Save candidate message with evaluation
            await MessageService.create_message(
                db,
                interview_id,
                MessageCreate(
                    role="candidate",
                    content=candidate_message.content,
                    question_number=question_number,
                    difficulty_level=interview.difficulty_start,
                    answer_quality_score=evaluation.score,
                    cheat_certainty=integrity.cheat_certainty if integrity else None,
                    telemetry=candidate_message.telemetry,
                ),
            )

            # Check if we've reached target questions
            questions_asked = len([m for m in messages if m.role == "assistant" and m.question_number])

            if questions_asked >= interview.target_questions:
                # Interview complete
                assistant_response = "Thank you for completing the interview! Your responses have been recorded and will be reviewed by our team."

                await MessageService.create_message(
                    db,
                    interview_id,
                    MessageCreate(
                        role="assistant",
                        content=assistant_response,
                    ),
                )

                return {
                    "response": assistant_response,
                    "interview_complete": True,
                    "evaluation": evaluation.model_dump(),
                }

            # Generate next question
            focus_areas = interview.match_analysis_json.get("focus_areas", [])
            chat_history = "\n".join([f"{m.role}: {m.content}" for m in messages])

            next_question = generate_question(
                focus_areas=focus_areas,
                difficulty_level=interview.difficulty_start,
                chat_history=chat_history,
                questions_asked=questions_asked,
            )

            # Save next question
            await MessageService.create_message(
                db,
                interview_id,
                MessageCreate(
                    role="assistant",
                    content=next_question,
                    question_number=question_number + 1,
                    difficulty_level=interview.difficulty_start,
                ),
            )

            return {
                "response": next_question,
                "interview_complete": False,
                "evaluation": evaluation.model_dump(),
                "next_question_number": question_number + 1,
            }

        elif classification.type == "Clarification":
            # Provide clarification (simple response for now)
            clarification_response = f"Let me clarify the question: {last_question}\n\nPlease provide your answer when you're ready."

            await MessageService.create_message(
                db,
                interview_id,
                MessageCreate(
                    role="candidate",
                    content=candidate_message.content,
                    telemetry=candidate_message.telemetry,
                ),
            )

            await MessageService.create_message(
                db,
                interview_id,
                MessageCreate(
                    role="assistant",
                    content=clarification_response,
                ),
            )

            return {
                "response": clarification_response,
                "interview_complete": False,
                "classification": "clarification",
            }

        else:  # OffTopic
            # Redirect to current question
            redirect_response = f"Let's stay focused on the current question: {last_question}"

            await MessageService.create_message(
                db,
                interview_id,
                MessageCreate(
                    role="candidate",
                    content=candidate_message.content,
                    telemetry=candidate_message.telemetry,
                ),
            )

            await MessageService.create_message(
                db,
                interview_id,
                MessageCreate(
                    role="assistant",
                    content=redirect_response,
                ),
            )

            return {
                "response": redirect_response,
                "interview_complete": False,
                "classification": "off_topic",
            }
