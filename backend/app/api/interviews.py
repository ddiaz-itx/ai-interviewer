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


@router.delete("/{interview_id}", status_code=204)
@limiter.limit(RATE_LIMIT_ADMIN)
async def delete_interview(
    request: Request,
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Delete an interview.

    Args:
        interview_id: Interview ID
        db: Database session

    Raises:
        HTTPException: If interview not found
    """
    deleted = await InterviewService.delete_interview(db, interview_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Interview not found")

    return None


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


@router.get("/{interview_id}/costs")
@limiter.limit(RATE_LIMIT_ADMIN)
async def get_interview_costs(
    request: Request,
    interview_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Get cost breakdown for a specific interview.

    Args:
        interview_id: Interview ID
        db: Database session

    Returns:
        Cost breakdown with token usage and estimated costs
    """
    from sqlalchemy import select, func
    from app.models.llm_usage import LLMUsage

    # Get all LLM usage for this interview
    result = await db.execute(
        select(LLMUsage).where(LLMUsage.interview_id == interview_id)
    )
    usage_records = result.scalars().all()

    if not usage_records:
        return {
            "interview_id": interview_id,
            "total_cost": 0.0,
            "total_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "by_agent": {},
        }

    # Aggregate by agent
    by_agent = {}
    total_cost = 0.0
    total_tokens = 0
    cache_hits = 0
    cache_misses = 0

    for record in usage_records:
        if record.cached:
            cache_hits += 1
        else:
            cache_misses += 1

        total_cost += record.estimated_cost
        total_tokens += record.total_tokens

        if record.agent_name not in by_agent:
            by_agent[record.agent_name] = {
                "calls": 0,
                "tokens": 0,
                "cost": 0.0,
                "cached": 0,
            }

        by_agent[record.agent_name]["calls"] += 1
        by_agent[record.agent_name]["tokens"] += record.total_tokens
        by_agent[record.agent_name]["cost"] += record.estimated_cost
        if record.cached:
            by_agent[record.agent_name]["cached"] += 1

    return {
        "interview_id": interview_id,
        "total_cost": round(total_cost, 6),
        "total_tokens": total_tokens,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_hit_rate": round((cache_hits / (cache_hits + cache_misses) * 100), 2) if (cache_hits + cache_misses) > 0 else 0,
        "by_agent": by_agent,
    }


@router.get("/stats/costs")
@limiter.limit(RATE_LIMIT_ADMIN)
async def get_cost_statistics(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    """
    Get aggregate cost statistics across all interviews.

    Returns:
        Aggregate cost statistics
    """
    from sqlalchemy import select, func
    from app.models.llm_usage import LLMUsage

    # Get aggregate statistics
    result = await db.execute(
        select(
            func.sum(LLMUsage.estimated_cost).label("total_cost"),
            func.sum(LLMUsage.total_tokens).label("total_tokens"),
            func.count(LLMUsage.id).label("total_calls"),
            func.sum(func.cast(LLMUsage.cached, sa.Integer)).label("cache_hits"),
        )
    )
    stats = result.one()

    total_cost = float(stats.total_cost or 0)
    total_tokens = int(stats.total_tokens or 0)
    total_calls = int(stats.total_calls or 0)
    cache_hits = int(stats.cache_hits or 0)
    cache_misses = total_calls - cache_hits

    return {
        "total_cost": round(total_cost, 6),
        "total_tokens": total_tokens,
        "total_calls": total_calls,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_hit_rate": round((cache_hits / total_calls * 100), 2) if total_calls > 0 else 0,
    }


@router.get("/cache/stats")
@limiter.limit(RATE_LIMIT_ADMIN)
async def get_cache_statistics(
    request: Request,
    current_user: dict = Depends(require_admin),
):
    """
    Get cache statistics.

    Returns:
        Cache statistics including hit rate and size
    """
    from app.utils.llm_cache import get_cache

    cache = get_cache()
    return cache.get_stats()
