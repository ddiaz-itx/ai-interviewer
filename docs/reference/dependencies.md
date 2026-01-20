# Dependency Checklist

This document tracks all dependencies and their purposes to ensure nothing is missing.

## Production Dependencies (`[tool.poetry.dependencies]`)

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| python | ^3.11 | Runtime | ✅ |
| fastapi | ^0.109.0 | Web framework | ✅ |
| uvicorn | ^0.27.0 | ASGI server | ✅ |
| sqlalchemy | ^2.0.25 | ORM | ✅ |
| asyncpg | ^0.29.0 | PostgreSQL async driver | ✅ |
| alembic | ^1.13.1 | Database migrations | ✅ |
| pydantic | ^2.5.3 | Data validation | ✅ |
| pydantic-settings | ^2.1.0 | Settings management | ✅ |
| langchain | ^0.1.0 | LLM framework | ✅ |
| langchain-openai | ^0.0.2 | OpenAI integration | ✅ |
| langchain-google-genai | ^0.0.6 | Gemini integration | ✅ |
| PyPDF2 | ^3.0.1 | PDF text extraction | ✅ |
| python-multipart | ^0.0.6 | File upload support | ✅ |
| python-jose | ^3.3.0 | JWT tokens | ✅ |
| passlib | ^1.7.4 | Password hashing | ✅ |
| python-dotenv | ^1.0.0 | Environment variables | ✅ |
| tenacity | ^8.2.3 | Retry logic | ✅ |

## Development Dependencies (`[tool.poetry.group.dev.dependencies]`)

| Package | Version | Purpose | Status |
|---------|---------|---------|--------|
| pytest | ^7.4.4 | Testing framework | ✅ |
| pytest-asyncio | ^0.23.3 | Async test support | ✅ |
| pytest-cov | ^4.1.0 | Test coverage | ✅ |
| httpx | ^0.26.0 | HTTP client for API tests | ✅ |
| aiosqlite | ^0.19.0 | SQLite async driver for tests | ✅ |
| black | ^24.1.1 | Code formatter | ✅ |
| ruff | ^0.1.14 | Linter | ✅ |
| mypy | ^1.8.0 | Type checker | ✅ |

## Installation Commands

### Install all dependencies
```bash
cd backend
poetry install
```

### Install production dependencies only
```bash
poetry install --only main
```

### Update dependencies
```bash
poetry update
```

### Add new dependency
```bash
# Production
poetry add package-name

# Development
poetry add --group dev package-name
```

## Dependency Verification

Run this to verify all dependencies are installed:

```bash
poetry show
```

Check for specific package:

```bash
poetry show aiosqlite
```

## Common Issues

### Module not found after adding to pyproject.toml

**Solution**: Run `poetry install` to actually install the package

```bash
cd backend
poetry install
```

### Poetry lock file out of sync

**Solution**: Update the lock file

```bash
poetry lock --no-update
poetry install
```

### Dependency conflicts

**Solution**: Check dependency tree

```bash
poetry show --tree
```
