# Implementation Notes & Reminders

## ⚠️ Items to Review Later

### 1. Pydantic Deprecation Warning
**Location**: `backend/app/schemas/interview.py:73`

**Issue**: 
```
Support for class-based `config` is deprecated, use ConfigDict instead.
Deprecated in Pydantic V2.0 to be removed in V3.0.
```

**Action**: Update to use `ConfigDict` instead of class-based config

**Priority**: Medium (works now, but will break in Pydantic V3)

---

### 2. Test State Transition Validation
**Location**: `backend/tests/test_api.py::TestInterviewEndpoints::test_assign_interview_invalid_state`

**Issue**:
```
StateTransitionError: Invalid transition from InterviewStatus.DRAFT to InterviewStatus.ASSIGNED
```

**Status**: ✅ This is actually CORRECT behavior! The test is validating that:
- You cannot assign an interview in DRAFT status
- You must upload documents and analyze them first (DRAFT → READY)
- Only then can you assign (READY → ASSIGNED)

**Action**: Update the test to expect this error OR test the correct flow

**Priority**: Low (test is working as designed, just needs better assertion)

**Suggested Fix**:
```python
async def test_assign_interview_invalid_state(self, client):
    """Test assigning interview in wrong state."""
    # Create interview (DRAFT status)
    create_response = await client.post(
        "/interviews/",
        json={"target_questions": 5, "difficulty_start": 5},
    )
    interview_id = create_response.json()["id"]

    # Try to assign (should fail - needs to be READY first)
    response = await client.post(f"/interviews/{interview_id}/assign")

    # Should return 400 with state transition error
    assert response.status_code == 400
    assert "Invalid transition" in response.json()["detail"]
```

---

## ✅ Completed Items

- [x] Fixed PyPDF2 import (was pypdf2)
- [x] Fixed AsyncClient for httpx tests
- [x] Added aiosqlite for test database
- [x] Switched tests to SQLite in-memory

---

## 📋 Phase Status

- [x] Phase 1: Environment & Infrastructure
- [x] Phase 2: Database Models & State Machine
- [x] Phase 3: LangChain Agents
- [x] Phase 4: Backend API
- [/] Phase 5: Frontend Development (IN PROGRESS)
- [ ] Phase 6: Testing & Verification
