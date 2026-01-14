# Authentication

## Admin Credentials

**Username**: `admin`  
**Password**: `admin123`

## How to Use

### 1. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Use Token for Admin Endpoints

Add the token to the `Authorization` header:

```bash
curl -X GET http://localhost:8000/interviews \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Frontend Integration

Update the API client to include the token:

```typescript
// Store token after login
localStorage.setItem('token', response.access_token);

// Add to API requests
const token = localStorage.getItem('token');
fetch('/interviews', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Protected Endpoints

All admin endpoints now require authentication:

- `POST /interviews` - Create interview
- `GET /interviews` - List interviews
- `GET /interviews/{id}` - Get interview
- `POST /interviews/{id}/upload` - Upload documents
- `POST /interviews/{id}/assign` - Assign interview
- `POST /interviews/{id}/complete` - Complete interview

## Public Endpoints

These endpoints do NOT require authentication:

- `POST /auth/login` - Login
- `POST /chat/start` - Start interview (uses token in URL)
- `POST /chat/message` - Send message (interview in progress)

## Security Notes

1. **Change the password** in production! Update `ADMIN_PASSWORD_HASH` in `app/api/auth.py`
2. **Set SECRET_KEY** in `.env` to a secure random string
3. **Token expiration**: Tokens expire after 24 hours (configurable in `app/config.py`)
4. **HTTPS only** in production to protect tokens in transit

## Generate Password Hash

To create a new password hash:

```python
from app.utils.auth import get_password_hash
print(get_password_hash("your-new-password"))
```
