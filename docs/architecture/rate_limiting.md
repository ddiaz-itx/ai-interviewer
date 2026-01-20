# Rate Limiting Implementation

## Overview

Rate limiting has been implemented across all API endpoints to protect against abuse and ensure fair usage.

## Rate Limits

| Endpoint | Limit | Reason |
|----------|-------|--------|
| `POST /auth/login` | 5/minute | Prevent brute force attacks |
| `POST /interviews/*` | 30/minute | Admin operations |
| `GET /interviews/*` | 30/minute | Admin operations |
| `POST /chat/start/{token}` | 60/minute | Allow conversation flow |
| `POST /chat/{id}/message` | 60/minute | Allow conversation flow |
| `GET /chat/{id}/messages` | 60/minute | Allow conversation flow |

## Implementation

### Technology

- **Library**: slowapi (FastAPI-compatible rate limiting)
- **Storage**: In-memory (suitable for single-instance deployments)
- **Key**: IP address (can be extended to user-based)

### Files Modified

1. `backend/pyproject.toml` - Added slowapi dependency
2. `backend/app/middleware/rate_limit.py` - Rate limiting configuration
3. `backend/app/api/auth.py` - Applied limits to login
4. `backend/app/api/interviews.py` - Applied limits to all admin endpoints
5. `backend/app/api/chat.py` - Applied limits to chat endpoints
6. `backend/app/main.py` - Integrated slowapi middleware

## Installation

```bash
cd backend
poetry lock
poetry install
```

## Testing Rate Limits

### Test Login Rate Limit (5/minute)

```bash
# This should fail on the 6th request within a minute
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "wrong"}' \
    && echo " - Request $i"
done
```

Expected: First 5 requests return 401, 6th returns 429 (Too Many Requests)

### Test Admin Endpoint (30/minute)

```bash
# Get a valid token first
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# Test rate limit
for i in {1..35}; do
  curl -X GET http://localhost:8000/interviews \
    -H "Authorization: Bearer $TOKEN" \
    && echo " - Request $i"
done
```

Expected: First 30 requests succeed, 31st returns 429

## Response Headers

When rate limited, the API returns:
- **Status Code**: 429 Too Many Requests
- **Headers**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## Production Considerations

### Upgrade to Redis

For multi-instance deployments, upgrade to Redis backend:

```python
# app/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)
```

### User-Based Rate Limiting

Add user-based limits in addition to IP:

```python
def get_user_identifier(request: Request):
    # Get user from JWT token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        payload = verify_token(token)
        return payload.get("sub", get_remote_address(request))
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_identifier)
```

### Whitelist Trusted IPs

```python
WHITELISTED_IPS = ["10.0.0.1", "192.168.1.1"]

def custom_key_func(request: Request):
    ip = get_remote_address(request)
    if ip in WHITELISTED_IPS:
        return None  # No rate limit
    return ip
```

## Benefits

✅ **Security**: Prevents brute force attacks on login
✅ **Stability**: Protects server from excessive requests
✅ **Fair Usage**: Ensures all users get equal access
✅ **Simple**: No external dependencies (in-memory)
✅ **Scalable**: Easy to upgrade to Redis for production
