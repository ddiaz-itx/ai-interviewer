# AI Interviewer

AI-powered technical interview platform that conducts adaptive interviews, evaluates candidate responses, detects integrity issues, and generates comprehensive reports.

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **PostgreSQL** (via Docker or local install)
- **Git**

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-interviewer
   ```

2. **Set up backend**:
   ```bash
   cd backend
   poetry install
   cp .env.example .env
   # Edit .env with your API keys
   poetry run alembic upgrade head
   ```

3. **Set up frontend**:
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   ```

4. **Start PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

5. **Run the application**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   poetry run uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

6. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

## Features

### Admin Features

- **Interview Creation**: Configure questions, difficulty, and upload documents
- **Document Analysis**: AI-powered resume-role matching
- **Interview Management**: Track status, view progress, assign to candidates
- **Comprehensive Reports**: Detailed evaluation with scores, gaps, and integrity flags

### Candidate Features

- **Secure Access**: Token-based interview links with 48-hour expiration
- **Adaptive Questioning**: Dynamic difficulty adjustment based on performance
- **Real-time Chat**: Natural conversation with AI interviewer
- **Integrity Monitoring**: Paste detection and response time tracking

### Technical Features

- **JWT Authentication**: Secure admin routes with token-based auth
- **Rate Limiting**: Protection against abuse (5/min login, 30/min admin, 60/min chat)
- **Database Indexing**: Optimized queries for performance
- **State Machine**: Robust interview workflow management
- **LLM Integration**: OpenAI and Google Gemini support
- **Async Architecture**: High-performance async/await throughout

## Architecture

### Backend (Python + FastAPI)

```
backend/
├── app/
│   ├── agents/          # LangChain AI agents
│   ├── api/             # FastAPI endpoints
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── utils/           # Utilities (auth, file upload, state machine)
│   ├── middleware/      # Rate limiting
│   ├── config.py        # Configuration
│   ├── database.py      # Database session
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── tests/               # Unit and integration tests
└── pyproject.toml       # Poetry dependencies
```

**Stack**:
- FastAPI (async)
- PostgreSQL + SQLAlchemy (async)
- LangChain (OpenAI, Google Gemini)
- Alembic (migrations)
- Pytest (testing)
- slowapi (rate limiting)
- Argon2 (password hashing)

### Frontend (React + TypeScript)

```
frontend/
├── src/
│   ├── api/             # API client with JWT token injection
│   ├── components/      # Reusable components (ProtectedRoute)
│   ├── contexts/        # React contexts (AuthContext)
│   ├── pages/           # Page components
│   │   ├── Login.tsx
│   │   ├── AdminDashboard.tsx
│   │   ├── CreateInterview.tsx
│   │   ├── InterviewDetails.tsx
│   │   └── CandidateInterview.tsx
│   ├── App.tsx          # Routing with protected routes
│   └── main.tsx         # Entry point
├── package.json
└── vite.config.ts
```

**Stack**:
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Router (routing)

### Database Schema

**interviews**:
- State machine: CREATED → READY → ASSIGNED → IN_PROGRESS → COMPLETED
- Stores: resume, role, job offering paths
- Match analysis JSON
- Candidate link token with expiration
- Final report JSON

**messages**:
- Chat transcript
- Question/answer tracking
- Quality scores
- Telemetry (response time, paste detection)

## API Endpoints

### Public Endpoints

- `POST /auth/login` - Admin login (rate limit: 5/min)
- `POST /chat/start/{token}` - Start interview (rate limit: 60/min)
- `POST /chat/{id}/message` - Send message (rate limit: 60/min)
- `GET /chat/{id}/messages` - Get messages (rate limit: 60/min)

### Protected Endpoints (Requires JWT)

- `POST /interviews` - Create interview (rate limit: 30/min)
- `GET /interviews` - List interviews (rate limit: 30/min)
- `GET /interviews/{id}` - Get interview details (rate limit: 30/min)
- `POST /interviews/{id}/upload` - Upload documents (rate limit: 30/min)
- `POST /interviews/{id}/assign` - Generate candidate link (rate limit: 30/min)
- `POST /interviews/{id}/complete` - Complete interview (rate limit: 30/min)

## Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_interviewer

# LLM API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Authentication
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

## Development

### Running Tests

```bash
cd backend
poetry run pytest
```

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback
poetry run alembic downgrade -1
```

### Code Quality

```bash
# Backend
poetry run ruff check .
poetry run mypy .

# Frontend
npm run lint
npm run type-check
```

## Documentation

- [Getting Started](docs/guides/setup.md)
- [User Manual](docs/guides/user_manual.md)
- [Deployment Guide (Docker)](docs/deployment/general.md)
- [Deployment Guide (k3s)](docs/deployment/k3s.md)
- [Architecture Overview](docs/architecture/overview.md)
- [AI Agents](docs/architecture/agents.md)
- [Authentication](docs/architecture/authentication.md)
- [Rate Limiting](docs/architecture/rate_limiting.md)
- [Database Schema](docs/architecture/database.md)

## Security Features

- JWT-based authentication for admin routes
- Argon2 password hashing (production-ready)
- Token expiration (48 hours for candidate links, 24 hours for admin JWT)
- Rate limiting on all endpoints
- Protected routes in frontend
- Database indexes for performance
- Input validation with Pydantic

## Production Deployment

### Backend

1. Set strong `SECRET_KEY` in environment
2. Enable Argon2 password hashing (see `docs/enable_password_hashing.md`)
3. Configure Redis for rate limiting (optional)
4. Set up proper CORS origins
5. Use production database
6. Enable HTTPS

### Frontend

1. Build production bundle: `npm run build`
2. Set production `VITE_API_URL`
3. Deploy to CDN or static hosting
4. Enable HTTPS

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
