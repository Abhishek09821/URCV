# URCV Quick Start Guide

Get URCV running locally in under 5 minutes.

## Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Git](https://git-scm.com/downloads)
- (Optional) Python 3.11+ and Node.js 18+ for manual setup

## 🚀 Fast Start (Docker)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd urcv
```

### 2. Set Up Environment
```bash
# Copy example environment file
cp backend/.env.example backend/.env

# (Optional) Edit backend/.env to add API keys
# ANTHROPIC_API_KEY=your-claude-api-key
# GEMINI_API_KEY=your-gemini-api-key
```

### 3. Start All Services
```bash
docker-compose up -d
```

This command starts:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis cache (port 6379)
- ✅ MinIO storage (ports 9000, 9001)
- ✅ Backend API (port 8000)
- ✅ Celery worker (background jobs)

### 4. Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 5. Verify Everything is Running
```bash
# Check service health
curl http://localhost:8000/api/v1/health/detailed

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "components": {
#     "database": {"status": "healthy"},
#     ...
#   }
# }
```

### 6. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | http://localhost:8000 | - |
| **API Docs (Swagger)** | http://localhost:8000/api/docs | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **PostgreSQL** | localhost:5432 | urcv_user / urcv_password |
| **Redis** | localhost:6379 | - |

## 🛠️ Manual Setup (Without Docker)

### Backend Setup

1. **Install PostgreSQL 15+**
   ```bash
   # macOS
   brew install postgresql@15
   brew services start postgresql@15
   
   # Create database
   createdb urcv_db
   createuser urcv_user -P  # Enter password: urcv_password
   ```

2. **Install Redis 7+**
   ```bash
   # macOS
   brew install redis
   brew services start redis
   ```

3. **Install Tesseract (for OCR)**
   ```bash
   # macOS
   brew install tesseract
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install tesseract-ocr
   ```

4. **Set up Python environment**
   ```bash
   cd backend
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

6. **Run migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start backend**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Start Celery worker** (in another terminal)
   ```bash
   cd backend
   source venv/bin/activate
   celery -A app.celery_app worker --loglevel=info
   ```

### Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

## 📝 Common Commands

### Docker Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Run migrations
docker-compose exec backend alembic upgrade head

# Access backend shell
docker-compose exec backend bash

# Access PostgreSQL
docker-compose exec postgres psql -U urcv_user -d urcv_db
```

### Database Commands
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

### Development Commands
```bash
# Format code
cd backend
black .

# Lint code
ruff check .

# Type check
mypy app

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

## 🧪 Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed

# View API docs (in browser)
open http://localhost:8000/api/docs
```

### Using Python
```python
import requests

# Basic health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Detailed health check
response = requests.get("http://localhost:8000/api/v1/health/detailed")
print(response.json())
```

### Using HTTPie
```bash
# Install httpie
pip install httpie

# Make requests
http GET http://localhost:8000/api/v1/health/detailed
```

## 📂 Project Structure

```
urcv/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations
│   ├── tests/           # Tests
│   └── requirements.txt
├── frontend/            # React frontend (coming soon)
├── docs/               # Documentation
├── docker-compose.yml  # Docker services
└── README.md
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Redis Connection Failed
```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### MinIO Not Starting
```bash
# Check MinIO logs
docker-compose logs minio

# Recreate MinIO
docker-compose rm -f minio
docker-compose up -d minio
```

### Migrations Failed
```bash
# Check current migration status
docker-compose exec backend alembic current

# Try downgrading and upgrading
docker-compose exec backend alembic downgrade -1
docker-compose exec backend alembic upgrade head

# If still failing, check database state
docker-compose exec postgres psql -U urcv_user -d urcv_db -c "\dt"
```

### Import Errors
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 🎯 Next Steps

1. ✅ **You have the backend running!**

2. **Explore the API**
   - Visit http://localhost:8000/api/docs
   - Try the health check endpoints
   - Review the OpenAPI schema

3. **Read the Documentation**
   - [Architecture](docs/ARCHITECTURE.md) - System design
   - [Database Schema](docs/DATABASE_SCHEMA.md) - DB structure
   - [Resume JSON Schema](docs/RESUME_JSON_SCHEMA.md) - Data model
   - [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md) - What's next

4. **Start Developing**
   - Check [IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)
   - Next feature: Authentication
   - See [backend/README.md](backend/README.md) for development guide

5. **Run Tests** (once tests are added)
   ```bash
   docker-compose exec backend pytest
   ```

## 📚 Additional Resources

- **PRD**: [PRD.md](PRD.md) - Complete product requirements
- **Build Summary**: [docs/BUILD_SUMMARY.md](docs/BUILD_SUMMARY.md) - What's been built
- **Backend Guide**: [backend/README.md](backend/README.md) - Backend development
- **Main README**: [README.md](README.md) - Project overview

## 💡 Tips

- Use the Swagger UI at http://localhost:8000/api/docs to test API endpoints
- Check logs with `docker-compose logs -f backend`
- Backend auto-reloads when you change Python files
- Use `docker-compose down -v` to reset everything (removes volumes)
- MinIO console at http://localhost:9001 lets you browse uploaded files

## 🎉 Success!

If you can see the API docs at http://localhost:8000/api/docs, you're all set! 

The backend is running, the database is ready, and you can start developing features.

**Happy coding! 🚀**
