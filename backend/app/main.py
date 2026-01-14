"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import interviews, messages, auth
from app.config import settings


app = FastAPI(
    title="AI Interviewer API",
    description="AI-powered technical interview platform",
    version="1.0.0",
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
app.include_router(messages.router)  # Mixed (some protected, some public)


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
