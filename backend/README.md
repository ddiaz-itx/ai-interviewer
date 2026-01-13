# AI Interviewer Backend

Backend API for the AI Interviewer Chatbot application.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration (database URL, API keys, etc.)

4. Start PostgreSQL:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
poetry run alembic upgrade head
```

6. Start the development server:
```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=app
```

## Code Quality

Format code:
```bash
poetry run black .
poetry run ruff --fix .
```

Type checking:
```bash
poetry run mypy .
```
