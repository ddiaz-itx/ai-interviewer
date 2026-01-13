# AI Interviewer - Development Setup & Testing Guide

This guide will help you set up the development environment and test the current implementation.

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Docker** and Docker Compose installed
- **Git** installed

## Quick Setup

### Option 1: Automated Setup (Recommended)

Run the complete setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Install Poetry (if needed)
2. Install Python dependencies
3. Create `.env` file
4. Start PostgreSQL with Docker
5. Run database migrations
6. Install frontend dependencies

### Option 2: Manual Setup

#### Backend Setup

1. **Install Poetry** (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. **Install backend dependencies**:
```bash
cd backend
poetry install
```

3. **Create environment file**:
```bash
cp .env.example .env
```

4. **Edit `.env` file** and add your API keys:
```bash
nano .env  # or use your preferred editor
```

Required variables:
- `OPENAI_API_KEY` (if using OpenAI)
- `GOOGLE_API_KEY` (if using Gemini)
- `DATABASE_URL` (already configured for local Docker)

5. **Start PostgreSQL**:
```bash
cd ..
docker-compose up -d
```

6. **Run database migrations**:
```bash
cd backend
poetry run alembic upgrade head
```

#### Frontend Setup

1. **Install dependencies**:
```bash
cd frontend
npm install
```

## Running the Application

### Start Backend Server

In one terminal:
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Start Frontend Server

In another terminal:
```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **App**: http://localhost:5173

## Testing the Current Setup

### 1. Test Backend Health

Open your browser or use curl:

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Test API Documentation

Visit http://localhost:8000/docs to see the interactive API documentation (Swagger UI).

### 3. Test Database Connection

Check if the database tables were created:

```bash
# Connect to PostgreSQL
docker exec -it ai-interviewer-db psql -U postgres -d ai_interviewer

# List tables
\dt

# You should see:
# - interviews
# - messages
# - alembic_version

# Exit
\q
```

### 4. Test Frontend

1. Open http://localhost:5173 in your browser
2. You should see the AI Interviewer homepage
3. Click "Admin Dashboard" - you should see "Coming Soon"

### 5. Test State Machine (Python REPL)

```bash
cd backend
poetry run python
```

```python
from app.utils.state_machine import InterviewStatus, InterviewStateMachine

# Test valid transition
print(InterviewStateMachine.can_transition(
    InterviewStatus.DRAFT, 
    InterviewStatus.READY
))  # Should print: True

# Test invalid transition
print(InterviewStateMachine.can_transition(
    InterviewStatus.DRAFT, 
    InterviewStatus.COMPLETED
))  # Should print: False
```

## Running Tests

### Backend Tests

```bash
cd backend
poetry run pytest -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Common Issues & Solutions

### Issue: Poetry not found after installation

**Solution**: Restart your terminal or add Poetry to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Issue: PostgreSQL connection refused

**Solution**: Ensure Docker is running and PostgreSQL container is up:
```bash
docker-compose ps
docker-compose up -d
```

### Issue: Port 8000 or 5173 already in use

**Solution**: Kill the process using the port:
```bash
# Find process on port 8000
lsof -ti:8000 | xargs kill -9

# Find process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Issue: Database migration fails

**Solution**: Reset the database:
```bash
docker-compose down -v
docker-compose up -d
cd backend
poetry run alembic upgrade head
```

## What's Working Now

✅ **Backend Infrastructure**
- FastAPI server with CORS
- Health check endpoints
- Database connection
- SQLAlchemy models (Interview, Message)
- State machine validation
- Pydantic schemas

✅ **Frontend Infrastructure**
- React app with TypeScript
- TailwindCSS styling
- React Router setup
- Basic homepage

✅ **Database**
- PostgreSQL running in Docker
- Migrations applied
- Tables created (interviews, messages)

## What's Not Implemented Yet

❌ **LangChain Agents** (Phase 3)
- Document analysis
- Answer evaluation
- Question generation
- Report generation

❌ **API Endpoints** (Phase 4)
- Interview CRUD
- Document upload
- Chat messages
- Report retrieval

❌ **Frontend Components** (Phase 6)
- Admin dashboard
- Interview creation form
- Candidate chat interface
- Report viewer

## Next Steps

After confirming everything works:

1. **Phase 3**: Implement LangChain agents
2. **Phase 4**: Build API endpoints
3. **Phase 5**: Create frontend components
4. **Phase 6**: End-to-end testing

## Useful Commands

```bash
# View backend logs
cd backend
poetry run uvicorn app.main:app --reload --log-level debug

# View database logs
docker-compose logs -f postgres

# Reset database
docker-compose down -v && docker-compose up -d

# Format backend code
cd backend
poetry run black .
poetry run ruff --fix .

# Type check backend
poetry run mypy .

# Frontend linting
cd frontend
npm run lint
```
