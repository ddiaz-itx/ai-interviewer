"""Rate limiting configuration for API endpoints."""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address


# Check if we're in testing mode
_testing = os.getenv("TESTING", "false").lower() == "true"

# Initialize rate limiter with in-memory storage
# Disable rate limiting during tests
limiter = Limiter(
    key_func=get_remote_address,
    enabled=not _testing,
)


# Rate limit configurations
RATE_LIMIT_AUTH = "5/minute"  # Strict limit for authentication (prevent brute force)
RATE_LIMIT_ADMIN = "30/minute"  # Moderate limit for admin operations
RATE_LIMIT_CHAT = "60/minute"  # Lenient limit for chat (allow conversation flow)
RATE_LIMIT_DEFAULT = "100/minute"  # Default limit for other endpoints
