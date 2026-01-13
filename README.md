# AI Interviewer Chatbot

AI-powered technical interview platform that conducts adaptive interviews, evaluates answers, and generates comprehensive reports.

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Docker** and Docker Compose
- **Git**

### Setup

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

If you don't have Python 3.11, install it first:

```bash
chmod +x install-python311.sh
./install-python311.sh
```

For detailed setup instructions, see [SETUP.md](SETUP.md).

## 📁 Project Structure

```
ai-interviewer/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API endpoints (coming soon)
│   │   ├── agents/            # LangChain agents (coming soon)
│   │   ├── services/          # Business logic (coming soon)
│   │   ├── utils/             # Utilities (state machine)
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database session
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit tests
│   ├── pyproject.toml         # Poetry dependencies
│   └── README.md
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components (coming soon)
│   │   ├── pages/             # Page components (coming soon)
│   │   ├── services/          # API client (coming soon)
│   │   ├── hooks/             # Custom hooks (coming soon)
│   │   ├── types/             # TypeScript types (coming soon)
│   │   ├── App.tsx            # Main app
│   │   └── main.tsx           # Entry point
│   ├── package.json           # npm dependencies
│   └── README.md
│
├── docs/                       # Documentation
│   ├── agents.md              # Agent specifications
│   ├── database.md            # Database schema
│   ├── instructions.md        # Development guidelines
│   └── project_roadmap.md     # Project roadmap
│
├── docker-compose.yml          # PostgreSQL container
├── setup.sh                    # Complete setup script
├── setup-backend.sh            # Backend setup script
├── setup-frontend.sh           # Frontend setup script
├── install-python311.sh        # Python 3.11 installer
├── SETUP.md                    # Setup guide
├── PYTHON_VERSION_FIX.md       # Python troubleshooting
└── README.md                   # This file
```

## 🏗️ Architecture

### Backend (Python + FastAPI)

- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy (async)
- **LLM Framework**: LangChain
- **Migrations**: Alembic
- **Testing**: Pytest

### Frontend (React + TypeScript)

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Routing**: React Router
- **HTTP Client**: Axios

### Database Schema

- **interviews**: Interview sessions with state machine
- **messages**: Chat transcript with telemetry

### State Machine

```
DRAFT → READY → ASSIGNED → IN_PROGRESS → COMPLETED
```

## 🎯 Features

### Implemented ✅

**Phase 1 & 2: Infrastructure**
- Backend infrastructure (FastAPI + SQLAlchemy async)
- Frontend infrastructure (React + TypeScript + Vite + TailwindCSS)
- Database models with 5-state machine validation
- Alembic migrations
- Pydantic schemas for API contracts
- Development environment setup scripts
- Unit tests for models and state machine

**Phase 3: LangChain Agents**
- **Document Analysis Agent**: Analyzes resume/role/job offering match with scoring
- **Answer Evaluation Agent**: Scores answers (1-10) with detailed rationale
- **Question Generation Agent**: Generates adaptive questions based on difficulty
- **Message Classification Agent**: Classifies messages as Answer/Clarification/OffTopic
- **Report Generation Agent**: Creates comprehensive final reports with integrity flags
- **Integrity Judgment Agent**: Optional per-message integrity assessment
- **LLM Factory**: Multi-provider support (OpenAI, Gemini, Ollama)
- **Base Agent Class**: Retry logic, error handling, and logging
- **Input Validators**: Pydantic validators for all agent inputs
- **Comprehensive Tests**: Unit tests with mocking and validation tests

**Phase 4: Backend API**
- Interview CRUD endpoints
- Document upload with PDF text extraction
- Interview workflow (DRAFT → READY → ASSIGNED → IN_PROGRESS → COMPLETED)
- Chat message processing with AI agents
- Report generation
- Integrity tracking (paste detection, response time)
- Integration tests with SQLite in-memory database

**Phase 5: Frontend** 🆕
- **Admin Dashboard**: List interviews with filtering and statistics
- **Create Interview**: Multi-step form (configure → upload → analyze)
- **Interview Details**: View match analysis, reports, and candidate links
- **Candidate Interview**: Real-time chat interface with telemetry
- **API Client**: Type-safe TypeScript client for all endpoints
- **Modern UI**: Glassmorphism design with smooth animations
- **Responsive**: Works on desktop and mobile

### Architecture Improvements ✅

- **Error Handling**: Automatic retry with exponential backoff (3 attempts)
- **Input Validation**: Pydantic validators prevent invalid data from reaching LLMs
- **Structured Logging**: Detailed logging for debugging and monitoring
- **Type Safety**: Full type hints and Pydantic schemas throughout
- **Testability**: Mockable agents with clear interfaces
- **Cost Awareness**: Token usage estimation in logs

### In Progress 🚧

- End-to-end testing
- Production deployment configuration

### Planned 📋

- Caching layer for LLM responses
- Rate limiting for API endpoints
- Cost tracking dashboard
- Email notifications
- Advanced analytics

## 🧪 Testing

### Run Backend Tests

```bash
cd backend

# Run all tests
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_agents.py -v

# Run specific test class
poetry run pytest tests/test_agents.py::TestInputValidators -v

# Skip integration tests (require LLM API)
poetry run pytest -v -m "not skip"
```

### Test Categories

- **Unit Tests**: Models, state machine, validators
- **Agent Tests**: Input validation, initialization, mocking
- **Integration Tests**: Skipped by default (require LLM API keys)

### Run Frontend Tests

```bash
cd frontend
npm test
```

### Test Coverage

Current coverage areas:
- ✅ Database models and state machine
- ✅ Input validators (Pydantic)
- ✅ Agent initialization
- ✅ Error handling
- ⏳ API endpoints (Phase 4)
- ⏳ Frontend components (Phase 5)

## 📚 Documentation

- **[docs/setup.md](docs/setup.md)** - Complete setup and testing guide
- **[docs/python_version_fix.md](docs/python_version_fix.md)** - Python version troubleshooting
- **[docs/architecture_review.md](docs/architecture_review.md)** - Architecture review and improvements
- **[docs/code_review.md](docs/code_review.md)** - Comprehensive code review
- **[docs/api_testing.md](docs/api_testing.md)** - API testing guide
- **[docs/dependencies.md](docs/dependencies.md)** - Dependency management
- **[docs/implementation_notes.md](docs/implementation_notes.md)** - Implementation reminders
- **[docs/agents.md](docs/agents.md)** - LangChain agent specifications
- **[docs/instructions.md](docs/instructions.md)** - Development guidelines
- **[docs/project_roadmap.md](docs/project_roadmap.md)** - Project roadmap
- **[docs/phase5_progress.md](docs/phase5_progress.md)** - Frontend development progress

## 🏛️ Architecture & Best Practices

### Design Principles

✅ **Separation of Concerns**
- Clear boundaries between models, schemas, agents, and APIs
- Each agent has a single, well-defined responsibility

✅ **Type Safety**
- Pydantic schemas for all data structures
- Type hints throughout the codebase
- Structured LLM outputs prevent parsing errors

✅ **Error Handling**
- Automatic retry with exponential backoff
- Graceful degradation on failures
- Detailed error logging

✅ **Input Validation**
- Pydantic validators for all agent inputs
- Prevents invalid data from reaching LLMs
- Clear validation error messages

✅ **Testability**
- Mockable dependencies
- Clear interfaces
- Comprehensive test coverage

✅ **Observability**
- Structured logging for all agent operations
- Token usage estimation
- Performance tracking

### Code Quality Standards

- **Type Safety**: All functions have type hints
- **Documentation**: Docstrings for all public APIs
- **Testing**: Unit tests for all core functionality
- **Validation**: Input validation before LLM calls
- **Error Handling**: Retry logic and graceful failures
- **Logging**: Structured logs for debugging

See [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) for detailed analysis and improvement recommendations.

## 🛠️ Development

### Start Backend

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

API available at:
- http://localhost:8000
- http://localhost:8000/docs (Swagger)

### Start Frontend

```bash
cd frontend
npm run dev
```

App available at: http://localhost:5173

### Database Management

```bash
# Start PostgreSQL
docker-compose up -d

# Stop PostgreSQL
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d
cd backend
poetry run alembic upgrade head
```

### Code Quality

```bash
# Backend
cd backend
poetry run black .
poetry run ruff --fix .
poetry run mypy .

# Frontend
cd frontend
npm run lint
```

## 🤝 Contributing

1. Follow the coding standards in [docs/instructions.md](docs/instructions.md)
2. Write tests for new features
3. Use conventional commits
4. Ensure all tests pass before committing

## 📝 License

This is a training project.

## 🔗 Related Documents

- [Implementation Plan](C:\Users\DDiaz\.gemini\antigravity\brain\938daba1-15c7-4cba-b07c-9990876fa01e\implementation_plan.md)
- [Task Breakdown](C:\Users\DDiaz\.gemini\antigravity\brain\938daba1-15c7-4cba-b07c-9990876fa01e\task.md)
- [Workflow Reference](C:\Users\DDiaz\.gemini\antigravity\brain\938daba1-15c7-4cba-b07c-9990876fa01e\workflow_reference.md)
