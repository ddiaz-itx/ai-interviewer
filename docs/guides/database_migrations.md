# Database Migration Guide

## Issue

Getting error: `column "token_expires_at" of relation "interviews" does not exist`

## Cause

The database schema is out of sync with the code. We added new columns but haven't run the migrations.

## Solution

Run the pending migrations to update the database schema.

### Step 1: Check Current Migration Status

```bash
cd backend
poetry run alembic current
```

### Step 2: Run Migrations

```bash
poetry run alembic upgrade head
```

This will apply:
- `002_add_composite_indexes.py` - Performance indexes
- `003_add_token_expiration.py` - Token expiration column

### Step 3: Verify

```bash
poetry run alembic current
```

Should show: `003_add_token_expiration (head)`

## Alternative: Reset Database (Development Only)

If you want to start fresh:

```bash
# Drop and recreate database
poetry run alembic downgrade base
poetry run alembic upgrade head
```

⚠️ **Warning**: This will delete all data!

## What the Migrations Add

### Migration 002: Composite Indexes
- `ix_interviews_status_created` - Filter by status + sort by date
- `ix_messages_interview_timestamp` - Get messages by interview + sort by time

### Migration 003: Token Expiration
- `token_expires_at` column to `interviews` table
- Allows 48-hour expiration on candidate links

## After Running Migrations

The application should work correctly. The error will be resolved.

## Troubleshooting

If migrations fail:

1. **Check database connection**:
   ```bash
   poetry run python -c "from app.database import engine; print('Connected!')"
   ```

2. **Check alembic version table**:
   ```sql
   SELECT * FROM alembic_version;
   ```

3. **Manual migration** (if needed):
   ```sql
   ALTER TABLE interviews ADD COLUMN token_expires_at TIMESTAMP WITH TIME ZONE;
   ```
