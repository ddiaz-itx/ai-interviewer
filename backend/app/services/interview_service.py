"""Interview service - business logic for interview operations."""
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import analyze_documents, generate_report
from app.models import Interview, Message
from app.schemas.interview import InterviewCreate, MatchAnalysis
from app.utils.state_machine import InterviewStatus, InterviewStateMachine


class InterviewService:
    """Service for interview business logic."""

    @staticmethod
    async def create_interview(
        db: AsyncSession, interview_data: InterviewCreate
    ) -> Interview:
        """
        Create a new interview in DRAFT status.

        Args:
            db: Database session
            interview_data: Interview creation data

        Returns:
            Created interview
        """
        interview = Interview(
            status=InterviewStatus.DRAFT.value,
            target_questions=interview_data.target_questions,
            difficulty_start=interview_data.difficulty_start,
        )

        db.add(interview)
        await db.commit()
        await db.refresh(interview)

        return interview

    @staticmethod
    async def upload_documents(
        db: AsyncSession,
        interview_id: int,
        resume_path: str,
        role_path: str,
        job_offering_path: str,
    ) -> Interview:
        """
        Upload documents to an interview.

        Args:
            db: Database session
            interview_id: Interview ID
            resume_path: Path to resume file
            role_path: Path to role description file
            job_offering_path: Path to job offering file

        Returns:
            Updated interview

        Raises:
            ValueError: If interview not found or not in DRAFT status
        """
        # Get interview
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        if interview.status != InterviewStatus.DRAFT.value:
            raise ValueError(f"Interview must be in DRAFT status to upload documents")

        # Update document paths
        interview.resume_path = resume_path
        interview.role_path = role_path
        interview.job_offering_path = job_offering_path

        await db.commit()
        await db.refresh(interview)

        return interview

    @staticmethod
    async def analyze_match(
        db: AsyncSession,
        interview_id: int,
        resume_text: str,
        role_text: str,
        job_offering_text: str,
    ) -> Interview:
        """
        Analyze candidate-role match and transition to READY status.

        Args:
            db: Database session
            interview_id: Interview ID
            resume_text: Resume text content
            role_text: Role description text content
            job_offering_text: Job offering text content

        Returns:
            Updated interview with match analysis

        Raises:
            ValueError: If interview not found or invalid state
        """
        # Get interview
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # Run document analysis agent
        match_analysis: MatchAnalysis = analyze_documents(
            resume_text, role_text, job_offering_text
        )

        # Update interview with match analysis
        interview.match_analysis_json = match_analysis.model_dump()

        # Transition to READY status
        InterviewStateMachine.transition(interview, InterviewStatus.READY)

        await db.commit()
        await db.refresh(interview)

        return interview

    @staticmethod
    async def assign_interview(db: AsyncSession, interview_id: int) -> Interview:
        """
        Generate candidate link token and transition to ASSIGNED status.

        Args:
            db: Database session
            interview_id: Interview ID

        Returns:
            Updated interview with candidate link token and expiration

        Raises:
            ValueError: If interview not found or invalid state
        """
        # Get interview
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # Generate secure token
        interview.candidate_link_token = secrets.token_urlsafe(32)
        # Token expires in 48 hours
        interview.token_expires_at = datetime.utcnow() + timedelta(hours=48)

        # Transition to ASSIGNED status
        InterviewStateMachine.transition(interview, InterviewStatus.ASSIGNED)

        await db.commit()
        await db.refresh(interview)

        return interview

    @staticmethod
    async def start_interview(db: AsyncSession, token: str) -> Interview:
        """
        Start interview session and transition to IN_PROGRESS status.

        Args:
            db: Database session
            token: Candidate link token

        Returns:
            Interview in IN_PROGRESS status

        Raises:
            ValueError: If token invalid, expired, or interview already started
        """
        # Find interview by token
        result = await db.execute(
            select(Interview).where(Interview.candidate_link_token == token)
        )
        interview = result.scalar_one_or_none()
        
        if not interview:
            raise ValueError("Invalid interview token")
        
        # Check if token has expired
        if interview.token_expires_at and interview.token_expires_at < datetime.now(interview.token_expires_at.tzinfo):
            raise ValueError("Interview link has expired. Please request a new link.")

        # Transition to IN_PROGRESS
        InterviewStateMachine.transition(interview, InterviewStatus.IN_PROGRESS)

        await db.commit()
        await db.refresh(interview)

        return interview

    @staticmethod
    async def get_interview(db: AsyncSession, interview_id: int) -> Optional[Interview]:
        """
        Get interview by ID.

        Args:
            db: Database session
            interview_id: Interview ID

        Returns:
            Interview or None if not found
        """
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_interview_by_token(db: AsyncSession, token: str) -> Optional[Interview]:
        """
        Get interview by candidate token.

        Args:
            db: Database session
            token: Candidate link token

        Returns:
            Interview or None if not found
        """
        result = await db.execute(
            select(Interview).where(Interview.candidate_link_token == token)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_interviews(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Interview]:
        """
        List all interviews with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of interviews
        """
        result = await db.execute(
            select(Interview).order_by(Interview.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def complete_interview(db: AsyncSession, interview_id: int) -> Interview:
        """
        Complete interview and generate final report.

        Args:
            db: Database session
            interview_id: Interview ID

        Returns:
            Completed interview with report

        Raises:
            ValueError: If interview not found or invalid state
        """
        # Get interview with messages
        result = await db.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        interview = result.scalar_one_or_none()

        if not interview:
            raise ValueError(f"Interview {interview_id} not found")

        # Get all messages
        messages_result = await db.execute(
            select(Message)
            .where(Message.interview_id == interview_id)
            .order_by(Message.timestamp)
        )
        messages = list(messages_result.scalars().all())

        # Build transcript
        transcript = "\n\n".join(
            [f"{msg.role.upper()}: {msg.content}" for msg in messages]
        )

        # Collect question scores
        question_scores = []
        for msg in messages:
            if msg.role == "candidate" and msg.answer_quality_score:
                question_scores.append({
                    "score": msg.answer_quality_score,
                    "rationale": f"Question {msg.question_number}",
                })

        # Build telemetry summary
        paste_count = sum(
            1 for msg in messages
            if msg.telemetry and msg.telemetry.get("paste_detected")
        )
        telemetry_summary = f"Total messages: {len(messages)}, Paste events: {paste_count}"

        # Generate report
        final_report = await generate_report(
            match_analysis=interview.match_analysis_json or {},
            transcript=transcript,
            question_scores=question_scores,
            telemetry_summary=telemetry_summary,
            db=db,
            interview_id=interview_id,
        )

        # Update interview
        interview.report_json = final_report.model_dump()

        # Transition to COMPLETED
        InterviewStateMachine.transition(interview, InterviewStatus.COMPLETED)

        await db.commit()
        await db.refresh(interview)

        return interview

    @staticmethod
    async def delete_interview(db: AsyncSession, interview_id: int) -> bool:
        """
        Delete an interview.

        Args:
            db: Database session
            interview_id: Interview ID

        Returns:
            True if deleted, False if not found
        """
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            return False

        await db.delete(interview)
        await db.commit()

        return True
