# URCV Backend

FastAPI-based backend for URCV - Universal Resume Conversion & Verification.

## Tech Stack

- **FastAPI 0.108+** - Modern async web framework
- **Python 3.11+** - Latest Python with great async support
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL 15+** - Primary database
- **Redis 7+** - Cache and message broker
- **Celery** - Async task queue
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation
- **PyMuPDF + pdfplumber** - PDF processing
- **Anthropic Claude** - AI improvements

## Project Structure

```
app/
├── api/                    # API layer
│   ├── routes/            # Route handlers
│   ├── dependencies/      # Dependency injection
│   └── middlewares/       # Custom middlewares
├── core/                  # Core configuration
│   ├── config.py         # Settings
│   ├── security.py       # Auth utilities
│   ├── exceptions.py     # Custom exceptions
│   └── logging.py        # Logging config
├── domain/               # Domain layer
│   ├── schemas/         # Resume JSON schema
│   └── rules/           # Business rules
├── infrastructure/       # Infrastructure layer
│   ├── database/        # SQLAlchemy models
│   ├── storage/         # S3 client
│   ├── cache/           # Redis client
│   ├── pdf_processor/   # PDF utilities
│   └── ai_client/       # AI service clients
├── features/            # Feature modules
│   ├── auth/           # Authentication
│   ├── resume/         # Resume management
│   ├── template/       # Template engine
│   ├── ats/            # ATS analysis
│   ├── ai/             # AI improvements
│   ├── export/         # Export generation
│   └── jd_matching/    # Job description matching
└── main.py             # Application entry point
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Tesseract OCR

### Installation

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install dev dependencies (optional)**
```bash
pip install -r requirements-dev.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one version
```bash
alembic downgrade -1
```

### Show current version
```bash
alembic current
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/unit/test_parser.py
```

## Code Quality

### Format code
```bash
black .
```

### Lint code
```bash
ruff check .
```

### Type checking
```bash
mypy app
```

### Run all checks
```bash
black . && ruff check . && mypy app && pytest
```

## Development

### Start with auto-reload
```bash
uvicorn app.main:app --reload --log-level debug
```

### Start Celery worker
```bash
celery -A app.celery_app worker --loglevel=info
```

### Access API documentation
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key (must be secure in production)
- `ANTHROPIC_API_KEY` - Claude API key
- `S3_ACCESS_KEY_ID` - S3 access key
- `S3_SECRET_ACCESS_KEY` - S3 secret key

## API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health with components
- `GET /api/v1/health/live` - Kubernetes liveness probe
- `GET /api/v1/health/ready` - Kubernetes readiness probe

### Authentication (Coming Soon)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Resumes (Coming Soon)
- `POST /api/v1/resumes/upload` - Upload PDF
- `GET /api/v1/resumes` - List user resumes
- `GET /api/v1/resumes/{id}` - Get resume details
- `PUT /api/v1/resumes/{id}` - Update resume
- `DELETE /api/v1/resumes/{id}` - Delete resume

### Templates (Coming Soon)
- `GET /api/v1/templates` - List templates
- `GET /api/v1/templates/{id}` - Get template details
- `POST /api/v1/templates/convert` - Convert resume to template

### ATS (Coming Soon)
- `POST /api/v1/ats/analyze/{resume_id}` - Analyze ATS score

### AI (Coming Soon)
- `POST /api/v1/ai/improve` - Improve section with AI

### Export (Coming Soon)
- `POST /api/v1/exports` - Generate export
- `GET /api/v1/exports/{id}` - Download export

## Architecture Principles

### Clean Architecture
- **Independence** from frameworks
- **Testability** without UI/DB
- **Clear boundaries** between layers
- **Dependency rule** - dependencies point inward

### SOLID Principles
- Single Responsibility
- Open/Closed
- Liskov Substitution
- Interface Segregation
- Dependency Inversion

### Key Design Decisions

1. **Async/Await Throughout** - FastAPI + SQLAlchemy async
2. **Feature-Based Organization** - Self-contained modules
3. **Pydantic Validation** - Runtime type checking
4. **Resume JSON as Source of Truth** - All operations use this schema
5. **Background Jobs** - Celery for long-running tasks
6. **Caching Strategy** - Redis for ATS scores and user data

## Performance

- Database connection pooling
- Redis caching layer
- Async I/O operations
- Background job processing
- Query optimization with indexes
- Response compression

## Security

- JWT authentication
- Password hashing (bcrypt)
- Rate limiting (slowapi)
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- CORS protection
- File type validation
- Audit logging

## Monitoring

- Structured JSON logging
- Sentry error tracking (production)
- Health check endpoints
- Request/response logging middleware

## Deployment

### Docker
```bash
docker build -t urcv-backend .
docker run -p 8000:8000 urcv-backend
```

### Railway
```bash
railway up
```

### Fly.io
```bash
fly deploy
```

## Troubleshooting

### Database connection issues
```bash
# Check PostgreSQL is running
pg_isready -U urcv_user -d urcv_db

# Test connection
python -c "from app.infrastructure.database import check_db_connection; import asyncio; print(asyncio.run(check_db_connection()))"
```

### Redis connection issues
```bash
# Check Redis is running
redis-cli ping

# Test connection
python -c "import redis; r = redis.from_url('redis://localhost:6379'); print(r.ping())"
```

### Import errors
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Contributing

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Format and lint code
5. Submit pull request

## License

MIT License - see [LICENSE](../LICENSE) for details.
