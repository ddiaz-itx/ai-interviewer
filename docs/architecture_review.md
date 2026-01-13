# Architecture Review & Improvements

## Current Architecture Assessment

### ✅ Strengths

1. **Separation of Concerns**
   - Clear separation between models, schemas, agents, and API layers
   - Each agent has a single, well-defined responsibility
   - Database layer properly abstracted

2. **Type Safety**
   - Pydantic schemas for all data structures
   - Type hints throughout the codebase
   - Structured LLM outputs prevent parsing errors

3. **Testability**
   - Agents are independent and mockable
   - Clear interfaces for each component
   - Dependency injection ready (LLM factory)

4. **Configuration Management**
   - Environment-based configuration
   - Centralized settings with Pydantic
   - Support for multiple LLM providers

5. **State Machine**
   - Explicit state transitions with validation
   - Preconditions enforced
   - Clear error messages

### ⚠️ Areas for Improvement

## 1. Error Handling & Resilience

**Issue**: Agents don't handle LLM failures gracefully

**Solution**: Add retry logic and fallbacks

```python
# app/agents/base.py
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseAgent:
    """Base class for all agents with retry logic."""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def invoke_with_retry(self, chain, inputs):
        """Invoke chain with automatic retry on failure."""
        try:
            return chain.invoke(inputs)
        except Exception as e:
            logger.error(f"Agent invocation failed: {e}")
            raise
```

## 2. Logging & Observability

**Issue**: No structured logging for debugging

**Solution**: Add comprehensive logging

```python
# app/utils/logging.py
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logger for agent operations."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_agent_call(self, agent_name: str, inputs: dict, outputs: dict):
        """Log agent invocation with inputs/outputs."""
        self.logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "inputs": inputs,
            "outputs": outputs
        }))
```

## 3. Caching

**Issue**: Repeated LLM calls for same inputs waste time/money

**Solution**: Add caching layer

```python
# app/utils/cache.py
from functools import lru_cache
import hashlib
import json

def cache_key(*args, **kwargs):
    """Generate cache key from arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()

# Usage in agents
@lru_cache(maxsize=100)
def cached_document_analysis(resume_hash: str, role_hash: str, job_hash: str):
    """Cached document analysis."""
    pass
```

## 4. Input Validation

**Issue**: No validation before sending to LLM

**Solution**: Add input validators

```python
# app/agents/validators.py
from pydantic import BaseModel, validator, Field

class DocumentInput(BaseModel):
    """Validated document input."""
    
    resume_text: str = Field(..., min_length=50, max_length=10000)
    role_text: str = Field(..., min_length=20, max_length=5000)
    job_text: str = Field(..., min_length=20, max_length=5000)
    
    @validator('*')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()
```

## 5. Rate Limiting

**Issue**: No protection against excessive LLM API calls

**Solution**: Add rate limiting

```python
# app/utils/rate_limiter.py
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    """Simple rate limiter for LLM calls."""
    
    def __init__(self, max_calls: int = 100, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = timedelta(seconds=window_seconds)
        self.calls = defaultdict(list)
    
    def check_rate_limit(self, key: str) -> bool:
        """Check if rate limit is exceeded."""
        now = datetime.utcnow()
        cutoff = now - self.window
        
        # Clean old calls
        self.calls[key] = [t for t in self.calls[key] if t > cutoff]
        
        if len(self.calls[key]) >= self.max_calls:
            return False
        
        self.calls[key].append(now)
        return True
```

## 6. Prompt Versioning

**Issue**: Prompt changes can break existing functionality

**Solution**: Version prompts

```python
# app/agents/prompts.py
PROMPT_VERSION = "1.0.0"

PROMPTS = {
    "document_analysis": {
        "v1.0.0": DOCUMENT_ANALYSIS_PROMPT,
        # Future versions can be added here
    }
}

def get_prompt(name: str, version: str = "1.0.0") -> str:
    """Get versioned prompt."""
    return PROMPTS[name][f"v{version}"]
```

## 7. Cost Tracking

**Issue**: No visibility into LLM API costs

**Solution**: Track token usage

```python
# app/utils/cost_tracker.py
class CostTracker:
    """Track LLM API costs."""
    
    COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    }
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for LLM call."""
        costs = self.COSTS.get(model, {"input": 0, "output": 0})
        return (input_tokens / 1000 * costs["input"]) + (output_tokens / 1000 * costs["output"])
```

## 8. Testing Improvements Needed

### Unit Tests
- ✅ Basic agent initialization
- ❌ Mock LLM responses and test logic
- ❌ Test error handling
- ❌ Test edge cases (empty inputs, malformed data)

### Integration Tests
- ❌ Test full agent chains
- ❌ Test with real LLM (optional, expensive)
- ❌ Test state machine transitions

### Performance Tests
- ❌ Measure LLM response times
- ❌ Test concurrent requests
- ❌ Memory usage profiling

## Priority Improvements

### High Priority (Implement Now)
1. ✅ Error handling with retries
2. ✅ Input validation
3. ✅ Structured logging
4. ✅ Comprehensive tests

### Medium Priority (Phase 4)
5. Caching layer
6. Rate limiting
7. Cost tracking

### Low Priority (Future)
8. Prompt versioning
9. Performance monitoring
10. A/B testing framework

## Recommended Next Steps

1. Implement base agent class with retry logic
2. Add input validators for all agents
3. Create comprehensive test suite
4. Add structured logging
5. Update documentation
