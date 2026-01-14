"""Interview API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.database import get_db
from app.middleware.rate_limit import limiter, RATE_LIMIT_ADMIN
from app.schemas.interview import (
    InterviewCreate,
    InterviewResponse,
    InterviewListResponse,
)
from app.services import InterviewService
from app.utils.file_upload import (
    save_upload_file,
    extract_text_from_pdf,
    validate_file_type,
    FileUploadError,
)

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", response_model=InterviewResponse, status_code=201)
@limiter.limit(RATE_LIMIT_ADMIN)
async def create_interview(
    request: Request,
    interview_data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Create a new interview in DRAFT status.

    Args:
        interview_data: Interview configuration
        db: Database session

    Returns:
        Created interview
    """
    interview = await InterviewService.create_interview(db, interview_data)
    return interview


@router.get("/", response_model=list[InterviewListResponse])
@limiter.limit(RATE_LIMIT_ADMIN)
async def list_interviews(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    List all interviews with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session

    Returns:
        List of interviews
    """
    interviews = await InterviewService.list_interviews(db, skip=skip, limit=limit)

    # Transform to list response
    return [
        InterviewListResponse(
            id=interview.id,
            status=interview.status,
            target_questions=interview.target_questions,
            match_score=interview.match_analysis_json.get("match_score") if interview.match_analysis_json else None,
            interview_score=interview.report_json.get("interview_score") if interview.report_json else None,
            created_at=interview.created_at,
        )
        for interview in interviews
    ]


@router.get("/{interview_id}", response_model=InterviewResponse)
@limiter.limit(RATE_LIMIT_ADMIN)
async def get_interview(
    request: Request,
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Get interview by ID.

    Args:
        interview_id: Interview ID
        db: Database session

    Returns:
        Interview details

    Raises:
        HTTPException: If interview not found
    """
    interview = await InterviewService.get_interview(db, interview_id)

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    return interview


@router.post("/{interview_id}/upload", response_model=InterviewResponse)
@limiter.limit(RATE_LIMIT_ADMIN)
async def upload_documents(
    request: Request,
    interview_id: int,
    resume: UploadFile = File(..., description="Candidate resume (PDF)"),
    role_description: UploadFile = File(..., description="Role description (PDF)"),
    job_offering: UploadFile = File(..., description="Job offering (PDF)"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Upload documents for an interview and run match analysis.

    This endpoint:
    1. Validates and saves the uploaded files
    2. Extracts text from PDFs
    3. Runs document analysis agent
    4. Transitions interview to READY status

    Args:
        interview_id: Interview ID
        resume: Resume PDF file
        role_description: Role description PDF file
        job_offering: Job offering PDF file
        db: Database session

    Returns:
        Updated interview with match analysis

    Raises:
        HTTPException: If validation fails or interview not found
    """
    try:
        # Validate file types
        for file in [resume, role_description, job_offering]:
            if not validate_file_type(file.filename or "", [".pdf"]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type for {file.filename}. Only PDF files are allowed.",
                )

        # Save files
        resume_path = await save_upload_file(resume, prefix="resume")
        role_path = await save_upload_file(role_description, prefix="role")
        job_path = await save_upload_file(job_offering, prefix="job")

        # Update interview with file paths
        interview = await InterviewService.upload_documents(
            db, interview_id, resume_path, role_path, job_path
        )

        # Extract text from PDFs
        resume_text = extract_text_from_pdf(resume_path)
        role_text = extract_text_from_pdf(role_path)
        job_text = extract_text_from_pdf(job_path)

        # Run match analysis
        interview = await InterviewService.analyze_match(
            db, interview_id, resume_text, role_text, job_text
        )

        return interview

    except FileUploadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/assign", response_model=InterviewResponse)
@limiter.limit(RATE_LIMIT_ADMIN)
async def assign_interview(
    request: Request,
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Generate candidate link and transition to ASSIGNED status.

    Args:
        interview_id: Interview ID
        db: Database session

    Returns:
        Interview with candidate link token

    Raises:
        HTTPException: If interview not found or invalid state
    """
    try:
        interview = await InterviewService.assign_interview(db, interview_id)
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{interview_id}/complete", response_model=InterviewResponse)
@limiter.limit(RATE_LIMIT_ADMIN)
async def complete_interview(
    request: Request,
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Complete interview and generate final report.

    Args:
        interview_id: Interview ID
        db: Database session

    Returns:
        Completed interview with report

    Raises:
        HTTPException: If interview not found or invalid state
    """
    try:
        interview = await InterviewService.complete_interview(db, interview_id)
        return interview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
