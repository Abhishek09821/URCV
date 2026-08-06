# Backend Setup Guide

## Quick Setup Options

### Option 1: Using Docker (Recommended - Easiest)

```bash
# Start all services
cd /Users/abhishektiwari/URCV
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Check if it worked
docker-compose exec backend alembic current
```

### Option 2: Local Python Setup

```bash
cd /Users/abhishektiwari/URCV/backend

# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Make sure PostgreSQL is running
# brew services start postgresql  # macOS
# sudo systemctl start postgresql  # Linux

# 4. Create database (if not exists)
createdb urcv_db
# or
psql -c "CREATE DATABASE urcv_db;"

# 5. Run migrations
alembic upgrade head

# 6. Check migration status
alembic current
```

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'sqlalchemy'"
**Solution**: Install dependencies first
```bash
pip install -r requirements.txt
```

### Issue 2: "Connection refused" or "could not connect to server"
**Solution**: Make sure PostgreSQL is running
```bash
# Check if PostgreSQL is running
brew services list  # macOS
# or
sudo systemctl status postgresql  # Linux

# Start PostgreSQL
brew services start postgresql@14  # macOS
# or
sudo systemctl start postgresql  # Linux
```

### Issue 3: "database 'urcv_db' does not exist"
**Solution**: Create the database
```bash
createdb urcv_db
# or
psql -c "CREATE DATABASE urcv_db;"
```

### Issue 4: "relation already exists"
**Solution**: Database already has tables, check current version
```bash
alembic current
# If shows version, you're good
# If you want fresh start:
alembic downgrade base
alembic upgrade head
```

### Issue 5: "Can't locate revision identified by 'xyz'"
**Solution**: Reset Alembic
```bash
# Drop and recreate database
dropdb urcv_db
createdb urcv_db

# Run migrations
alembic upgrade head
```

## Verify Setup

```bash
# 1. Check Alembic version
alembic current

# 2. Check tables created
psql urcv_db -c "\dt"

# Should see these tables:
# - users
# - resumes
# - templates
# - exports
# - job_descriptions
# - jd_matches
# - ai_improvements
# - verification_sessions
# - refresh_tokens
# - audit_logs
```

## Environment Variables

Make sure your `.env` file has:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=urcv_user
POSTGRES_PASSWORD=urcv_password
POSTGRES_DB=urcv_db
POSTGRES_PORT=5432
```

## Database Connection String

The app builds this automatically:
```
postgresql+asyncpg://urcv_user:urcv_password@localhost:5432/urcv_db
```

For Alembic (sync version):
```
postgresql://urcv_user:urcv_password@localhost:5432/urcv_db
```

## Need Help?

1. Check logs: `docker-compose logs backend`
2. Test config: `python3 -c "from app.core.config import settings; print(settings.DATABASE_URL)"`
3. Test DB connection: `psql -h localhost -U urcv_user -d urcv_db`
