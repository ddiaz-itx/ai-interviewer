# Project Instructions & Best Practices

## Project Purpose
[cite_start]To build a training-oriented AI Interviewer Chatbot that screens candidates based on a resume and role description[cite: 217].

## Tech Stack
- **Backend**: Python 3.11+, FastAPI, Poetry.
- **Database**: PostgreSQL, SQLAlchemy (Async), Alembic.
- **AI/LLM**: LangChain (for orchestration), Pydantic (for structured output).
- **Frontend**: React, TypeScript, TailwindCSS.
- **Testing**: Pytest (Backend), React Testing Library (Frontend).

## coding Standards
1. **Type Safety**: strict type hinting in Python, strict types in TypeScript.
2. **Documentation**: All API endpoints must have docstrings.
3. **Testing**: Every functional module must have a corresponding test file.
4. **Configuration**: Use `.env` for secrets (OpenAI API Key, DB URL). Never commit secrets.
5. **Git**: Use Conventional Commits (e.g., `feat: add interview model`, `fix: state transition bug`).

## Architecture Constraints
- **Separation of Concerns**: Keep LLM logic (chains/prompts) separate from API route handlers.
- **State Management**: The Interview State Machine is strict. An interview cannot move to `IN_PROGRESS` without `match_analysis` being present.
- **Formatting**: Use Black/Ruff for Python and Prettier for JS.