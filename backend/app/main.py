"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import interviews, chat, auth
from app.config import settings
from app.middleware.rate_limit import limiter


app = FastAPI(
    title="AI Interviewer API",
    description="AI-powered technical interview platform",
    version="1.0.0",
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from app.utils.state_machine import StateTransitionError

@app.exception_handler(StateTransitionError)
async def state_transition_exception_handler(request: Request, exc: StateTransitionError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)  # Public auth endpoints
app.include_router(interviews.router)  # Admin endpoints (protected)
app.include_router(chat.router)  # Chat endpoints (public for candidates)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Interviewer API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
