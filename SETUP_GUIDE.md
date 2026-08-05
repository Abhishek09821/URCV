# URCV Complete Setup Guide

## 🎯 Goal
Get URCV backend running locally in under 10 minutes.

---

## 📋 Prerequisites Check

Run this to verify prerequisites:
```bash
# Check Docker
docker --version
docker-compose --version

# Check Python (if running without Docker)
python3 --version  # Should be 3.11+

# Check PostgreSQL (if running without Docker)
psql --version     # Should be 15+
```

---

## 🚀 Setup Method 1: Docker (RECOMMENDED)

### Step 1: Clone & Navigate
```bash
cd /Users/abhishektiwari/URCV
```

### Step 2: Configure Environment
```bash
cd backend
cp .env.example .env
```

**Edit `.env` if needed:**
- Default values work with Docker
- Add `ANTHROPIC_API_KEY` for AI features (optional)

### Step 3: Start All Services
```bash
cd ..  # Back to project root
docker-compose up -d
```

**This starts:**
- PostgreSQL (localhost:5432)
- Redis (localhost:6379)
- MinIO S3 (localhost:9000, 9001)
- Backend API (localhost:8000)
- Celery worker

### Step 4: Initialize Database
```bash
# Option A: Create tables directly
docker-compose exec backend python scripts/init_db.py

# Option B: Use Alembic migrations (recommended)
docker-compose exec backend alembic upgrade head
```

### Step 5: Verify Everything Works
```bash
# Check if services are healthy
docker-compose exec backend python scripts/verify_setup.py

# Test the API
docker-compose exec backend python scripts/test_api.py
```

### Step 6: Access Services
```bash
# Open API documentation
open http://localhost:8000/api/docs

# Or test health endpoint
curl http://localhost:8000/health
```

**Service URLs:**
- 📡 API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/api/docs
- 🔍 Health: http://localhost:8000/api/v1/health/detailed
- 📦 MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
- 🗄️ PostgreSQL: localhost:5432 (urcv_user/urcv_password)
- 🔴 Redis: localhost:6379

### Common Docker Commands
```bash
# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# Access backend shell
docker-compose exec backend bash

# Access PostgreSQL
docker-compose exec postgres psql -U urcv_user -d urcv_db
```

---

## 🔧 Setup Method 2: Manual (Without Docker)

### Step 1: Install Dependencies

**PostgreSQL 15+:**
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Linux
sudo apt-get install postgresql-15
sudo systemctl start postgresql
```

**Redis 7+:**
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

**Python 3.11+:**
```bash
# macOS
brew install python@3.11

# Linux
sudo apt-get install python3.11
```

**Tesseract (for OCR):**
```bash
# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr
```

### Step 2: Set Up Database
```bash
# Create database and user
createdb urcv_db
createuser urcv_user -P  # Password: urcv_password
psql -d urcv_db -c "GRANT ALL PRIVILEGES ON DATABASE urcv_db TO urcv_user;"
```

### Step 3: Set Up Python Environment
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env

# Edit .env with your settings:
# - DATABASE_URL=postgresql+asyncpg://urcv_user:urcv_password@localhost:5432/urcv_db
# - REDIS_URL=redis://localhost:6379/0
# - SECRET_KEY=<generate-a-secure-key>
# - S3_ENDPOINT_URL=  (leave empty for local testing without S3)
```

### Step 5: Initialize Database
```bash
# Option A: Direct creation
python scripts/init_db.py

# Option B: Alembic migrations
alembic upgrade head
```

### Step 6: Start Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: (Optional) Start Celery Worker
```bash
# In another terminal
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

### Step 8: Verify
```bash
# In another terminal
python scripts/verify_setup.py
python scripts/test_api.py

# Or use curl
curl http://localhost:8000/health
```

---

## ✅ Verification Checklist

After setup, verify these work:

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. Detailed Health
```bash
curl http://localhost:8000/api/v1/health/detailed
# Expected: JSON with database status
```

### 3. API Documentation
```bash
open http://localhost:8000/api/docs
# Should open Swagger UI
```

### 4. Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'
# Expected: User data with id
```

### 5. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
# Expected: access_token and refresh_token
```

---

## 🐛 Troubleshooting

### Issue: Port 8000 already in use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or change port
uvicorn app.main:app --port 8001
```

### Issue: Database connection failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres  # If using Docker

# Or
pg_isready -U urcv_user -d urcv_db  # If manual setup

# Check connection string in .env
grep DATABASE_URL backend/.env
```

### Issue: Redis connection failed
```bash
# Check if Redis is running
docker-compose ps redis  # If using Docker

# Or
redis-cli ping  # Should return PONG

# Check connection string
grep REDIS_URL backend/.env
```

### Issue: MinIO not accessible
```bash
# Restart MinIO
docker-compose restart minio minio-setup

# Check logs
docker-compose logs minio
```

### Issue: Import errors
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment (if manual setup)
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Alembic migration fails
```bash
# Check current version
alembic current

# If stuck, create tables directly
python scripts/init_db.py

# Or reset (CAUTION: deletes data)
docker-compose down -v  # If using Docker
docker-compose up -d
alembic upgrade head
```

### Issue: API returns 500 errors
```bash
# Check logs
docker-compose logs backend  # If using Docker

# Or check uvicorn console output

# Common causes:
# 1. Database not initialized
# 2. Environment variables missing
# 3. Redis not running
```

---

## 🧪 Testing the API

### Using Swagger UI (Easiest)
1. Open http://localhost:8000/api/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"

### Using curl

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!","full_name":"Test"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}'
```

**Get Current User:**
```bash
# Save token from login response
TOKEN="your-access-token-here"

curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python script
```bash
cd backend
python scripts/test_api.py
```

---

## 📊 Development Workflow

### 1. Make Code Changes
Edit files in `backend/app/`

### 2. Server Auto-Reloads
If running with `--reload`, changes apply automatically

### 3. Check Logs
```bash
# Docker
docker-compose logs -f backend

# Manual
# Check uvicorn console output
```

### 4. Test Changes
```bash
# Quick test
curl http://localhost:8000/health

# Full test
python scripts/test_api.py
```

### 5. Create Migration (if models changed)
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 🔑 Important Configuration

### Required Environment Variables
```bash
SECRET_KEY=your-secret-key-min-32-characters
POSTGRES_SERVER=localhost
POSTGRES_USER=urcv_user
POSTGRES_PASSWORD=urcv_password
POSTGRES_DB=urcv_db
```

### Optional but Recommended
```bash
# AI Features
ANTHROPIC_API_KEY=sk-ant-...

# Production Settings
ENVIRONMENT=production
DEBUG=false
SENTRY_DSN=https://...
```

### S3 Configuration
```bash
# For local development (MinIO)
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_USE_SSL=false

# For production (AWS S3)
S3_ENDPOINT_URL=  # Leave empty
S3_ACCESS_KEY_ID=your-aws-key
S3_SECRET_ACCESS_KEY=your-aws-secret
S3_USE_SSL=true
```

---

## 📈 What to Do Next

### 1. Explore API Documentation
```bash
open http://localhost:8000/api/docs
```

### 2. Test All Endpoints
- Register user
- Login
- Upload resume (requires PDF file)
- Get resume data
- Analyze ATS score
- Generate AI improvement
- Export to PDF

### 3. Check Implementation
Read `BACKEND_COMPLETE.md` for full feature list

### 4. Start Frontend Development
See frontend README (when available)

### 5. Deploy to Production
See deployment guide (when available)

---

## 🎓 Understanding the System

### Architecture
```
User Request
    ↓
FastAPI (app/main.py)
    ↓
Routes (app/api/routes/)
    ↓
Services (app/features/*/service.py)
    ↓
Database (PostgreSQL) / Storage (S3)
```

### Key Directories
- `app/core/` - Configuration, security, logging
- `app/domain/` - Business logic, Resume JSON schema
- `app/features/` - Feature modules (auth, resume, ats, ai, export)
- `app/infrastructure/` - External services (DB, S3, AI)
- `app/api/` - API routes and middlewares
- `alembic/` - Database migrations
- `scripts/` - Utility scripts

### Data Flow
1. **Upload PDF** → S3 storage
2. **Parse PDF** → Extract text → Apply rules → Generate Resume JSON
3. **Store** → PostgreSQL (JSONB column)
4. **Edit** → Update Resume JSON
5. **Analyze** → ATS engine → Score + suggestions
6. **Improve** → Claude API → AI suggestions
7. **Export** → Generate PDF → S3 storage

---

## 🚀 Ready to Launch!

If everything works:
- ✅ Health check returns healthy
- ✅ Can register and login
- ✅ API docs accessible
- ✅ Database connected
- ✅ Redis connected

**You're ready to build amazing resume features!**

For issues, check:
1. This guide's Troubleshooting section
2. `BACKEND_COMPLETE.md` for implementation details
3. Docker logs: `docker-compose logs backend`
4. Database: `docker-compose exec postgres psql -U urcv_user -d urcv_db`

Happy coding! 🎉
