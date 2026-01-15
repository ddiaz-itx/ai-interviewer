# Deployment Guide

This guide covers how to deploy the AI Interviewer application to a production environment.

## Prerequisites

- **Docker** and **Docker Compose**
- **Node.js 18+** (for frontend build)
- **Python 3.11+** (for backend)
- **PostgreSQL 15+**
- **LLM API Keys** (OpenAI, Gemini)

---

## 1. Environment Configuration

Create a `.env` file in the `backend/` directory based on `.env.example`:

```ini
# Database
DATABASE_URL=postgresql+asyncpg://user:password@db_host:5432/ai_interviewer

# Security
SECRET_KEY=your-secure-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CANDIDATE_TOKEN_EXPIRE_HOURS=24
ADMIN_USER="admin"
ADMIN_PASSWORD_HASH="hashed_password_using_argon2"

# LLM Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=["https://your-domain.com"]

# Caching & Costs
CACHE_ENABLED=True
CACHE_TTL_SECONDS=3600
COST_TRACKING_ENABLED=True
```

---

## 2. Docker Deployment (Recommended)

### Build and Run

1. **Build Images**:
   ```bash
   docker-compose -f docker-compose.prod.yml build
   ```

2. **Start Services**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Run Migrations**:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

### Docker Compose Production File (`docker-compose.prod.yml`)

Ensure you have a production compose file that:
- Uses multi-stage builds for smaller images
- Sets `NODE_ENV=production` for frontend
- Mounts necessary volumes for persistent data (DB, logs)
- Restarts containers on failure

---

## 3. Manual Deployment

### Backend

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install poetry
   poetry install --only main
   ```

2. **Run Migrations**:
   ```bash
   poetry run alembic upgrade head
   ```

3. **Start Server (Gunicorn/Uvicorn)**:
   ```bash
   poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```
   *Note: Use a process manager like Supervisor or Systemd to keep it running.*

### Frontend

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Build for Production**:
   ```bash
   npm run build
   ```

3. **Serve Static Files**:
   Serve the `dist/` folder using Nginx, Apache, or a static site host (Vercel, Netlify).

   **Nginx Example**:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }

       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 4. Verification

1. **Health Check**:
   Visit `https://your-domain.com/api/health` (if implemented) or check logs.

2. **Admin Login**:
   Ensure you can log in to the admin dashboard.

3. **Test Interview**:
   Create a dummy interview and verify the candidate link works.

---

## 5. Maintenance

- **Backups**: regularly backup your PostgreSQL database.
- **Logs**: Monitor application logs for errors (`docker-compose logs -f`).
- **Updates**: Pull latest code, rebuild images, and run migrations.
