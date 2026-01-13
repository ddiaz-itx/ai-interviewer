"""Message/Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import generate_introduction
from app.database import get_db
from app.schemas.message import CandidateMessageSubmit, MessageResponse
from app.services import InterviewService, MessageService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/start/{token}")
async def start_interview(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Start interview session using candidate token.

    This endpoint:
    1. Validates the token
    2. Transitions interview to IN_PROGRESS
    3. Generates introduction message
    4. Generates first question

    Args:
        token: Candidate link token
        db: Database session

    Returns:
        Introduction and first question

    Raises:
        HTTPException: If token invalid or interview already started
    """
    try:
        # Start interview
        interview = await InterviewService.start_interview(db, token)

        # Generate introduction
        role_text = extract_text_from_pdf(interview.role_path) if interview.role_path else "the position"
        introduction = generate_introduction(
            role_description=role_text,
            target_questions=interview.target_questions,
        )

        # Save introduction message
        from app.schemas.message import MessageCreate
        await MessageService.create_message(
            db,
            interview.id,
            MessageCreate(
                role="assistant",
                content=introduction,
            ),
        )

        # Generate first question
        from app.agents import generate_question
        focus_areas = interview.match_analysis_json.get("focus_areas", ["General"])

        first_question = generate_question(
            focus_areas=focus_areas,
            difficulty_level=interview.difficulty_start,
            chat_history="",
            questions_asked=0,
        )

        # Save first question
        await MessageService.create_message(
            db,
            interview.id,
            MessageCreate(
                role="assistant",
                content=first_question,
                question_number=1,
                difficulty_level=interview.difficulty_start,
            ),
        )

        return {
            "interview_id": interview.id,
            "introduction": introduction,
            "first_question": first_question,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{interview_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    interview_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all messages for an interview.

    Args:
        interview_id: Interview ID
        db: Database session

    Returns:
        List of messages
    """
    messages = await MessageService.get_messages(db, interview_id)
    return messages


@router.post("/{interview_id}/message")
async def send_message(
    interview_id: int,
    message: CandidateMessageSubmit,
    db: AsyncSession = Depends(get_db),
):
    """
    Send candidate message and get AI response.

    This is the main interview loop endpoint that:
    1. Classifies the message (Answer/Clarification/OffTopic)
    2. Evaluates answers and generates next questions
    3. Handles clarifications and redirects

    Args:
        interview_id: Interview ID
        message: Candidate message with telemetry
        db: Database session

    Returns:
        AI response and metadata

    Raises:
        HTTPException: If interview not found or not in progress
    """
    try:
        response = await MessageService.process_candidate_message(
            db, interview_id, message
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Helper function (should be in utils)
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    from app.utils.file_upload import extract_text_from_pdf as extract
    try:
        return extract(file_path)
    except Exception:
        return "Role description"
