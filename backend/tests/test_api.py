"""Integration tests for API endpoints."""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.utils.state_machine import InterviewStatus


# Use SQLite in-memory database for tests (no setup required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine):
    """Create test database session factory."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    return async_session


@pytest_asyncio.fixture
async def client(test_db):
    """Create test client."""
    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    
    # Disable rate limiting for tests
    from app.middleware.rate_limit import limiter
    limiter._enabled = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    # Re-enable after tests
    limiter._enabled = True
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_token(client):
    """Get admin authentication token."""
    response = await client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.asyncio
class TestInterviewEndpoints:
    """Test interview endpoints."""

    async def test_create_interview(self, client, admin_token):
        """Test creating an interview."""
        response = await client.post(
            "/interviews/",
            json={"target_questions": 5, "difficulty_start": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == InterviewStatus.DRAFT.value
        assert data["target_questions"] == 5
        assert data["difficulty_start"] == 5
        assert "id" in data

    async def test_list_interviews(self, client, admin_token):
        """Test listing interviews."""
        # Create an interview first
        await client.post(
            "/interviews/",
            json={"target_questions": 5, "difficulty_start": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # List interviews
        response = await client.get(
            "/interviews/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_interview(self, client, admin_token):
        """Test getting interview by ID."""
        # Create interview
        create_response = await client.post(
            "/interviews/",
            json={"target_questions": 5, "difficulty_start": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        interview_id = create_response.json()["id"]

        # Get interview
        response = await client.get(
            f"/interviews/{interview_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == interview_id

    async def test_get_nonexistent_interview(self, client, admin_token):
        """Test getting non-existent interview."""
        response = await client.get(
            "/interviews/999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 404

    async def test_delete_interview(self, client, admin_token):
        """Test deleting an interview."""
        # Create interview
        create_response = await client.post(
            "/interviews/",
            json={"target_questions": 5, "difficulty_start": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        interview_id = create_response.json()["id"]

        # Delete interview
        response = await client.delete(
            f"/interviews/{interview_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 204

        # Verify it's gone
        response = await client.get(
            f"/interviews/{interview_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 404

    @pytest.mark.skip(reason="Requires actual PDF files and LLM API")
    async def test_upload_documents(self, client, admin_token):
        """Test document upload (requires real files)."""
        # This test would require actual PDF files
        # and LLM API key to run
        pass

    async def test_assign_interview_invalid_state(self, client, admin_token):
        """Test assigning interview in wrong state."""
        # Create interview (DRAFT status)
        create_response = await client.post(
            "/interviews/",
            json={"target_questions": 5, "difficulty_start": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        interview_id = create_response.json()["id"]

        # Try to assign (should fail - needs to be READY first)
        response = await client.post(
            f"/interviews/{interview_id}/assign",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 400


@pytest.mark.asyncio
class TestChatEndpoints:
    """Test chat endpoints."""

    async def test_start_interview_invalid_token(self, client):
        """Test starting interview with invalid token."""
        response = await client.post("/chat/start/invalid_token")

        assert response.status_code == 400

    async def test_get_messages_empty(self, client, admin_token):
        """Test getting messages for interview with no messages."""
        # Create interview
        create_response = await client.post(
            "/interviews/",
            json={"target_questions": 5, "difficulty_start": 5},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        interview_id = create_response.json()["id"]

        # Get messages
        response = await client.get(f"/chat/{interview_id}/messages")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.skip(reason="Requires interview in IN_PROGRESS state")
    async def test_send_message(self, client):
        """Test sending candidate message."""
        # This test requires setting up a complete interview flow
        # which involves LLM API calls
        pass


@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health and root endpoints."""

    async def test_root(self, client):
        """Test root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    async def test_health(self, client):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
