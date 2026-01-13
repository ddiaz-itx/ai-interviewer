# API Testing Guide

This guide provides instructions for testing the AI Interviewer API endpoints.

## Prerequisites

1. **Backend server running**:
   ```bash
   cd backend
   poetry run uvicorn app.main:app --reload
   ```

2. **Database running**:
   ```bash
   docker-compose up -d
   ```

3. **Environment configured**:
   - `.env` file with LLM API keys
   - Database migrations applied

## API Base URL

```
http://localhost:8000
```

## Testing Flow

### 1. Create Interview

```bash
curl -X POST http://localhost:8000/interviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "target_questions": 5,
    "difficulty_start": 5
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "status": "DRAFT",
  "target_questions": 5,
  "difficulty_start": 5,
  "created_at": "2026-01-13T20:00:00Z",
  ...
}
```

**Save the `id` for next steps!**

### 2. Upload Documents

You'll need 3 PDF files:
- `resume.pdf` - Candidate resume
- `role.pdf` - Role description
- `job.pdf` - Job offering

```bash
curl -X POST http://localhost:8000/interviews/1/upload \
  -F "resume=@/path/to/resume.pdf" \
  -F "role_description=@/path/to/role.pdf" \
  -F "job_offering=@/path/to/job.pdf"
```

**Expected Response:**
```json
{
  "id": 1,
  "status": "READY",
  "match_analysis_json": {
    "match_score": 8,
    "match_summary": "Strong candidate...",
    "focus_areas": ["Python", "FastAPI", "Testing"]
  },
  ...
}
```

**Note**: This step runs the Document Analysis Agent, so it requires an LLM API key.

### 3. List Interviews

```bash
curl http://localhost:8000/interviews/
```

### 4. Get Interview Details

```bash
curl http://localhost:8000/interviews/1
```

### 5. Assign Interview (Generate Candidate Link)

```bash
curl -X POST http://localhost:8000/interviews/1/assign
```

**Expected Response:**
```json
{
  "id": 1,
  "status": "ASSIGNED",
  "candidate_link_token": "abc123...",
  ...
}
```

**Save the `candidate_link_token`!**

### 6. Start Interview (Candidate Side)

```bash
curl -X POST http://localhost:8000/chat/start/abc123...
```

**Expected Response:**
```json
{
  "interview_id": 1,
  "introduction": "Hello! I'm your AI interviewer...",
  "first_question": "Can you explain your experience with Python?"
}
```

### 7. Get Messages

```bash
curl http://localhost:8000/chat/1/messages
```

### 8. Send Candidate Answer

```bash
curl -X POST http://localhost:8000/chat/1/message \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I have 5 years of Python experience working with FastAPI and Django...",
    "telemetry": {
      "response_time_ms": 15000,
      "paste_detected": false
    }
  }'
```

**Expected Response:**
```json
{
  "response": "Great! Can you describe a challenging problem you solved?",
  "interview_complete": false,
  "evaluation": {
    "score": 7,
    "rationale": "Good answer showing practical experience",
    "evidence": "mentioned FastAPI and Django",
    "followup_hint": null
  },
  "next_question_number": 2
}
```

### 9. Complete Interview

After answering all questions:

```bash
curl -X POST http://localhost:8000/interviews/1/complete
```

**Expected Response:**
```json
{
  "id": 1,
  "status": "COMPLETED",
  "report_json": {
    "interview_score": 7,
    "summary": "Candidate demonstrated...",
    "gaps": ["Could improve on..."],
    "meeting_expectations": ["Strong Python skills"],
    "integrity_flags": []
  },
  ...
}
```

## Interactive API Documentation

FastAPI provides interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these for easier testing with a UI!

## Common Issues

### 1. LLM API Key Not Set

**Error**: `ValueError: OPENAI_API_KEY not configured`

**Solution**: Add your API key to `.env`:
```bash
OPENAI_API_KEY=sk-...
```

### 2. Database Not Running

**Error**: Connection refused

**Solution**:
```bash
docker-compose up -d
```

### 3. Migrations Not Applied

**Error**: Table doesn't exist

**Solution**:
```bash
cd backend
poetry run alembic upgrade head
```

### 4. File Upload Fails

**Error**: Invalid file type

**Solution**: Ensure files are PDF format

## Test Data

Sample test files are available in `backend/tests/fixtures/`:
- `sample_resume.pdf`
- `sample_role.pdf`
- `sample_job.pdf`

## Automated Testing

Run integration tests:

```bash
cd backend
poetry run pytest tests/test_api.py -v
```

## Performance Testing

Test response times:

```bash
time curl -X POST http://localhost:8000/interviews/1/message \
  -H "Content-Type: application/json" \
  -d '{"content": "Test answer", "telemetry": {"response_time_ms": 1000, "paste_detected": false}}'
```

## Security Testing

1. **Test invalid tokens**:
   ```bash
   curl -X POST http://localhost:8000/chat/start/invalid_token
   ```
   Should return 400 error

2. **Test state transitions**:
   ```bash
   # Try to assign a DRAFT interview (should fail)
   curl -X POST http://localhost:8000/interviews/1/assign
   ```

## Monitoring

Watch logs in real-time:

```bash
# Backend logs
tail -f backend/logs/app.log

# Or run with verbose logging
poetry run uvicorn app.main:app --reload --log-level debug
```
