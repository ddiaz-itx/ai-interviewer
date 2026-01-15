"""Pytest configuration and shared fixtures."""
import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

# Set testing environment variable to disable rate limiting
# MUST be set before importing app modules
os.environ["TESTING"] = "true"

from app.database import Base, get_db
from app.main import app
from app.models.interview import Interview


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Disable rate limiting for tests
    from app.middleware.rate_limit import limiter
    limiter._enabled = False
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Re-enable rate limiting after tests
    limiter._enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_token(test_client: AsyncClient) -> str:
    """Get an admin authentication token using hardcoded credentials."""
    # Use the hardcoded admin credentials from auth.py
    response = await test_client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def test_interview(test_db: AsyncSession) -> Interview:
    """Create a test interview."""
    interview = Interview(
        status="DRAFT",
        target_questions=8,
        difficulty_start=5,
    )
    test_db.add(interview)
    await test_db.commit()
    await test_db.refresh(interview)
    return interview


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "match_score": 85,
        "summary": "Strong candidate with relevant experience",
        "focus_areas": ["Python", "FastAPI", "PostgreSQL"],
    }


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years Python development
    - FastAPI and Django experience
    - PostgreSQL database design
    
    Skills: Python, FastAPI, PostgreSQL, Docker, AWS
    """


@pytest.fixture
def sample_role_text():
    """Sample role description for testing."""
    return """
    Senior Backend Engineer
    
    Requirements:
    - 3+ years Python experience
    - FastAPI or similar framework
    - Database design experience
    - Cloud deployment knowledge
    """


@pytest.fixture
def sample_job_offering_text():
    """Sample job offering for testing."""
    return """
    We are seeking a Senior Backend Engineer to join our team.
    
    Responsibilities:
    - Design and implement REST APIs
    - Database architecture
    - Cloud infrastructure management
    
    Benefits:
    - Competitive salary
    - Remote work
    - Health insurance
    """
