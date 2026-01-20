# Re-enabling Password Hashing - Production Guide

## Current Status

✅ **Authentication works** with plain text password comparison (development only)
⚠️ **Not secure** for production use

## Steps to Re-enable Bcrypt Hashing

### 1. Verify Dependencies Are Correct

The `pyproject.toml` already has the correct bcrypt version pinned:
```toml
bcrypt = "4.0.1"  # Compatible with passlib
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
```

### 2. Generate a Fresh Password Hash

Run this command in the backend directory:

```bash
cd backend
poetry run python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(ctx.hash('admin123'))"
```

This will output something like:
```
$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Update auth.py

Replace the plain text check in `backend/app/api/auth.py`:

**Current (line 56):**
```python
# Simple password check for MVP
if login_data.password != "admin123":
```

**Replace with:**
```python
if not verify_password(login_data.password, ADMIN_PASSWORD_HASH):
```

**And update the hash constant (line 30):**
```python
ADMIN_PASSWORD_HASH = "$2b$12$YOUR_GENERATED_HASH_HERE"
```

### 4. Test the Authentication

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Should return a JWT token.

## Why It Will Work Now

1. **Correct bcrypt version**: We pinned bcrypt to 4.0.1 which is compatible with passlib
2. **Password length handling**: The `verify_password()` function in `app/utils/auth.py` already handles the 72-byte limit
3. **Error handling**: Try/catch blocks prevent crashes on bcrypt errors

## Alternative: Use Argon2 (Recommended for Production)

Argon2 is more modern and doesn't have the 72-byte limitation:

### Update pyproject.toml:
```toml
passlib = {extras = ["argon2"], version = "^1.7.4"}
argon2-cffi = "^23.1.0"
```

### Update app/utils/auth.py:
```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

### Generate hash:
```bash
poetry run python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['argon2'], deprecated='auto'); print(ctx.hash('admin123'))"
```

## Security Best Practices for Production

1. **Never hardcode passwords** - Store hashed passwords in database
2. **Use environment variables** for admin credentials
3. **Implement password policies** - minimum length, complexity requirements
4. **Add rate limiting** - prevent brute force attacks
5. **Use HTTPS only** - protect credentials in transit
6. **Implement account lockout** - after N failed attempts
7. **Add password reset flow** - with email verification

## Quick Fix Script

I've created `backend/enable_bcrypt.py` to automate this:

```python
#!/usr/bin/env python3
"""Enable bcrypt password hashing."""
import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate hash
password = "admin123"
hash_value = pwd_context.hash(password)

print("=" * 60)
print("Bcrypt Password Hash Generated")
print("=" * 60)
print(f"\nPassword: {password}")
print(f"Hash: {hash_value}")
print("\n" + "=" * 60)
print("Update backend/app/api/auth.py:")
print("=" * 60)
print(f'\nADMIN_PASSWORD_HASH = "{hash_value}"')
print("\nAnd replace line 56:")
print("if not verify_password(login_data.password, ADMIN_PASSWORD_HASH):")
print("=" * 60)
```

Run with: `poetry run python enable_bcrypt.py`
