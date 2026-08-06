# URCV - Quick Start Guide

Get the complete URCV application running in 5 minutes!

---

## Prerequisites

- **Docker** and **Docker Compose** installed
- **Node.js 18+** installed
- **Terminal** access

---

## Option 1: Docker (Recommended - Fastest)

### Step 1: Start Backend Services

```bash
# Navigate to project
cd /Users/abhishektiwari/URCV

# Start all backend services (PostgreSQL, Redis, MinIO, Backend API)
docker-compose up -d

# Wait for services to be ready (10-15 seconds)
sleep 15

# Run database migrations
docker-compose exec backend alembic upgrade head

# Verify backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Step 2: Start Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Create environment file
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

### Step 3: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

---

## Option 2: Manual Setup (Development)

### Step 1: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=urcv_user
POSTGRES_PASSWORD=urcv_password
POSTGRES_DB=urcv_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# S3 (MinIO)
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=urcv-files

# Security
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Optional: AI Features
# ANTHROPIC_API_KEY=your_claude_api_key_here
EOF

# Start PostgreSQL (if not running)
# brew services start postgresql@14  # macOS
# sudo systemctl start postgresql    # Linux

# Create database
createdb urcv_db

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

### Step 2: Setup Frontend

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Create .env
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
```

---

## First Steps

### 1. Register an Account

1. Open http://localhost:3000
2. Click "Sign up"
3. Fill in:
   - Full Name: John Doe
   - Email: john@example.com
   - Password: password123
4. Click "Create Account"
5. You'll be auto-logged in

### 2. Upload Your First Resume

1. Click "Upload Resume" button
2. Drag and drop a PDF resume (or click to browse)
3. Click "Upload & Parse Resume"
4. Wait 2-3 seconds for parsing
5. View parsed data with confidence scores

### 3. Edit Resume Data

1. From dashboard, click on your resume
2. Click "Edit Resume" button
3. Click section tabs (Personal, Summary, Skills, etc.)
4. Edit any field
5. Click "Save Changes"

### 4. Run ATS Analysis

1. From resume detail page
2. Click "Show ATS Analysis"
3. View overall score and category breakdown
4. See keywords found/missing
5. Read improvement suggestions

### 5. Generate AI Improvements (Optional)

> **Note**: Requires ANTHROPIC_API_KEY in backend .env

1. Click "AI Improvements"
2. Select section to improve (Summary, Experience, etc.)
3. Choose improvement types (Grammar, Action Verbs, etc.)
4. Click "Generate AI Improvement"
5. Review before/after comparison
6. Click "Apply" or "Reject"

### 6. Export Resume

1. Click "Export" button
2. Choose format (PDF - ATS-optimized)
3. Click "Export as PDF"
4. File downloads automatically
5. View export history

---

## Verify Everything Works

Run this checklist:

```bash
# Backend health check
curl http://localhost:8000/health
# ✅ Should return: {"status":"healthy"}

# Frontend running
curl http://localhost:3000
# ✅ Should return HTML

# Database connection
docker-compose exec backend python -c "from app.infrastructure.database import check_db_connection; import asyncio; print(asyncio.run(check_db_connection()))"
# ✅ Should return: True

# API docs accessible
open http://localhost:8000/api/docs
# ✅ Should open Swagger UI
```

---

## Common Issues & Solutions

### Issue: Port 8000 already in use
```bash
# Find process
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or change port in docker-compose.yml
```

### Issue: PostgreSQL connection failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Issue: Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/.env
# Ensure BACKEND_CORS_ORIGINS includes http://localhost:3000

# Restart backend
docker-compose restart backend
```

### Issue: npm install fails
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: Build fails
```bash
# Check Node version
node --version
# Should be 18 or higher

# Update Node if needed
# nvm install 18
# nvm use 18
```

---

## Stop All Services

```bash
# Stop frontend (Ctrl+C in terminal)

# Stop backend services
docker-compose down

# Or stop and remove volumes (fresh start)
docker-compose down -v
```

---

## Production Build

### Frontend
```bash
cd frontend
npm run build
# Creates optimized build in dist/

# Preview production build
npm run preview
```

### Backend
```bash
# Already production-ready with Docker
docker build -t urcv-backend ./backend
docker run -p 8000:8000 urcv-backend
```

---

## Environment Variables Reference

### Backend (.env)

**Required:**
```env
SECRET_KEY=your-secret-key-32-chars-minimum
POSTGRES_SERVER=localhost
POSTGRES_USER=urcv_user
POSTGRES_PASSWORD=urcv_password
POSTGRES_DB=urcv_db
REDIS_HOST=localhost
REDIS_PORT=6379
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=urcv-files
```

**Optional:**
```env
ANTHROPIC_API_KEY=sk-ant-...     # For AI improvements
SENTRY_DSN=https://...            # For error tracking
SMTP_HOST=smtp.gmail.com          # For email notifications
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Next Steps

1. ✅ Application running
2. ✅ Test all features
3. ✅ Upload a real resume
4. ✅ Try all operations
5. → Read full documentation (BACKEND_COMPLETE.md, FRONTEND_COMPLETE.md)
6. → Configure production deployment
7. → Add custom templates
8. → Integrate with job boards

---

## Support

### Documentation
- **README.md** - Project overview
- **BACKEND_COMPLETE.md** - Backend details
- **FRONTEND_COMPLETE.md** - Frontend details
- **PROJECT_STATUS.md** - Overall status

### API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Logs
```bash
# Backend logs
docker-compose logs -f backend

# PostgreSQL logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

---

## Success!

If you can:
1. ✅ See login page at http://localhost:3000
2. ✅ Register and login successfully
3. ✅ Upload a PDF resume
4. ✅ See parsed resume data
5. ✅ Edit and save changes
6. ✅ Export a PDF

**Congratulations! URCV is fully operational! 🎉**

---

**Ready to launch!** 🚀
