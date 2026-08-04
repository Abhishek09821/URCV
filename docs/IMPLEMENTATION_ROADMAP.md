# URCV Implementation Roadmap

## Current Status ✓

### Phase 0: Architecture & Foundation (COMPLETED)

#### Documentation ✓
- [x] Complete PRD Analysis
- [x] System Architecture Document
- [x] Database Schema Design
- [x] Resume JSON Schema Specification
- [x] Project Structure Document
- [x] Implementation Roadmap

#### Backend Foundation ✓
- [x] Project structure created
- [x] `pyproject.toml` with all dependencies
- [x] `requirements.txt` and `requirements-dev.txt`
- [x] Core configuration (`app/core/config.py`)
- [x] Environment variables (`.env.example`)
- [x] Security utilities (`app/core/security.py`)
- [x] Custom exceptions (`app/core/exceptions.py`)
- [x] Logging configuration (`app/core/logging.py`)
- [x] Resume JSON Schema as Pydantic models (`app/domain/schemas/resume_schema.py`)

## Next Steps

### Phase 1: Backend Core (IN PROGRESS)

#### 1.1 Database Layer
```python
# Files to create:
app/infrastructure/database/
├── __init__.py
├── base.py          # Base model class
├── session.py       # Database session management
└── models.py        # SQLAlchemy models (User, Resume, Template, etc.)

# Alembic migrations
alembic/
├── versions/
│   └── 001_initial_schema.py
└── env.py
```

#### 1.2 Storage Infrastructure
```python
app/infrastructure/storage/
├── __init__.py
├── base.py          # Abstract storage interface
├── s3.py            # S3/MinIO implementation
└── local.py         # Local filesystem (development)
```

#### 1.3 Cache Layer
```python
app/infrastructure/cache/
├── __init__.py
└── redis.py         # Redis client and utilities
```

#### 1.4 API Foundation
```python
app/api/
├── dependencies/
│   ├── __init__.py
│   ├── auth.py      # get_current_user, require_auth
│   ├── database.py  # get_db session
│   └── services.py  # service dependencies
├── middlewares/
│   ├── __init__.py
│   ├── auth.py      # JWT middleware
│   ├── error_handler.py  # Global error handler
│   ├── logging.py   # Request/response logging
│   └── rate_limit.py     # Rate limiting
└── routes/
    ├── __init__.py
    └── health.py    # Health check endpoint
```

#### 1.5 FastAPI Application
```python
app/
├── __init__.py
└── main.py          # FastAPI app initialization
```

### Phase 2: Authentication & User Management

#### 2.1 Auth Feature
```python
app/features/auth/
├── __init__.py
├── service.py       # AuthService (register, login, refresh)
├── schemas.py       # Login, Register, Token schemas
└── utils.py         # Token utilities

app/api/routes/
└── auth.py          # Auth endpoints
```

#### 2.2 User Model Complete
- Implement CRUD operations
- Email verification
- Password reset

### Phase 3: PDF Processing & Resume Parser

#### 3.1 PDF Processor Infrastructure
```python
app/infrastructure/pdf_processor/
├── __init__.py
├── extractor.py     # PyMuPDF + pdfplumber
├── ocr.py           # Tesseract OCR
└── generator.py     # PDF generation (ReportLab/WeasyPrint)
```

#### 3.2 Resume Parser Feature
```python
app/features/resume/parser/
├── __init__.py
├── pipeline.py      # Main parsing pipeline
├── extractors/
│   ├── text_extractor.py
│   ├── ocr_extractor.py
│   └── ai_extractor.py
├── rules/
│   ├── email_rule.py
│   ├── phone_rule.py
│   ├── date_rule.py
│   └── section_rule.py
├── confidence.py    # Confidence scoring
└── normalizer.py    # Data normalization
```

#### 3.3 Resume Service
```python
app/features/resume/
├── __init__.py
├── service.py       # ResumeService (CRUD, parse, verify)
├── schemas.py       # API schemas
└── tasks.py         # Celery async tasks

app/api/routes/
└── resume.py        # Resume endpoints
```

### Phase 4: Template Engine

#### 4.1 Template Engine Core
```python
app/features/template/engine/
├── __init__.py
├── converter.py     # Main conversion logic
├── mapper.py        # Resume JSON → Template mapping
├── layout_calculator.py
├── overflow_detector.py
└── renderer.py      # HTML/PDF rendering
```

#### 4.2 Template Definitions
```python
app/features/template/templates/
├── __init__.py
├── base.py          # BaseTemplate class
├── amity.py         # Amity University template
├── generic.py       # Generic template
└── ats_optimized.py # ATS-optimized template
```

#### 4.3 Template Service
```python
app/features/template/
├── __init__.py
├── service.py       # TemplateService
└── schemas.py       # Template schemas

app/api/routes/
└── template.py      # Template endpoints
```

### Phase 5: ATS Analysis Engine

#### 5.1 ATS Checks
```python
app/features/ats/engine/checks/
├── __init__.py
├── contact_check.py
├── section_check.py
├── formatting_check.py
├── keyword_check.py
└── readability_check.py
```

#### 5.2 ATS Service
```python
app/features/ats/
├── __init__.py
├── service.py       # ATSService
├── engine/
│   ├── analyzer.py
│   └── scorer.py
└── schemas.py

app/api/routes/
└── ats.py           # ATS endpoints
```

### Phase 6: AI Services

#### 6.1 AI Client Infrastructure
```python
app/infrastructure/ai_client/
├── __init__.py
├── base.py          # Abstract AI client
├── claude.py        # Anthropic Claude
└── gemini.py        # Google Gemini
```

#### 6.2 AI Improvement Feature
```python
app/features/ai/improver/
├── __init__.py
├── project_improver.py
├── experience_improver.py
├── summary_improver.py
└── prompts.py       # Prompt templates
```

#### 6.3 AI Service
```python
app/features/ai/
├── __init__.py
├── service.py       # AIService
└── schemas.py

app/api/routes/
└── ai.py            # AI endpoints
```

### Phase 7: Export Engine

#### 7.1 Export Generators
```python
app/features/export/generators/
├── __init__.py
├── pdf_generator.py
├── docx_generator.py
└── ats_pdf_generator.py
```

#### 7.2 Export Service
```python
app/features/export/
├── __init__.py
├── service.py       # ExportService
└── schemas.py

app/api/routes/
└── export.py        # Export endpoints
```

### Phase 8: Job Description Matching

```python
app/features/jd_matching/
├── __init__.py
├── service.py       # JDMatchingService
├── matcher.py       # Matching algorithm
└── schemas.py

app/api/routes/
└── jd.py            # JD endpoints
```

### Phase 9: Frontend Development

#### 9.1 Frontend Foundation
```bash
# Initialize React + TypeScript + Vite
cd frontend
npm create vite@latest . -- --template react-ts
npm install

# Install dependencies
npm install \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  axios \
  react-hook-form \
  zod \
  @hookform/resolvers \
  tailwindcss \
  @radix-ui/react-* \
  lucide-react \
  date-fns \
  clsx \
  class-variance-authority

# Setup Tailwind + shadcn/ui
npx tailwindcss init -p
npx shadcn-ui@latest init
```

#### 9.2 Frontend Structure
```typescript
src/
├── components/ui/       # shadcn/ui components
├── features/
│   ├── auth/
│   ├── dashboard/
│   ├── resume/
│   ├── template/
│   ├── ats/
│   └── export/
├── lib/                 # Configurations
├── hooks/               # Custom hooks
├── services/            # API services
├── store/               # Zustand stores
└── types/               # TypeScript types
```

#### 9.3 Core Features Implementation Order
1. Authentication (Login, Register)
2. Dashboard
3. Resume Upload & Parser UI
4. Resume Editor (structured forms)
5. Template Converter
6. ATS Analysis UI
7. Export UI
8. Settings

### Phase 10: Testing

#### 10.1 Backend Tests
```python
tests/
├── unit/
│   ├── test_parser.py
│   ├── test_ats.py
│   ├── test_template.py
│   └── test_ai.py
├── integration/
│   ├── test_api_auth.py
│   ├── test_api_resume.py
│   └── test_pipeline.py
└── e2e/
    └── test_user_flow.py
```

#### 10.2 Frontend Tests
```typescript
tests/
└── playwright/
    ├── auth.spec.ts
    ├── resume-upload.spec.ts
    ├── resume-editor.spec.ts
    └── template-conversion.spec.ts
```

### Phase 11: DevOps & Deployment

#### 11.1 Docker Setup
```yaml
# docker-compose.yml for local development
services:
  backend:
  frontend:
  postgres:
  redis:
  minio:
  celery:
```

#### 11.2 CI/CD Pipelines
```yaml
.github/workflows/
├── backend-ci.yml    # Test, lint, build backend
├── frontend-ci.yml   # Test, lint, build frontend
└── deploy.yml        # Deploy to production
```

#### 11.3 Deployment
- Frontend: Vercel
- Backend: Railway / Fly.io
- Database: Neon / Supabase
- Storage: AWS S3
- Redis: Upstash / Railway

### Phase 12: Production Readiness

- [ ] Security audit
- [ ] Performance optimization
- [ ] Load testing
- [ ] Monitoring setup (Sentry)
- [ ] Analytics (PostHog)
- [ ] Documentation
- [ ] User guide
- [ ] API documentation (OpenAPI)

## Implementation Priority

### Must Have (MVP - Phase 1-7)
1. ✓ Architecture & Database Schema
2. ✓ Resume JSON Schema
3. Authentication
4. Resume Upload
5. PDF Parser
6. Resume Editor
7. Template Engine (1-2 templates)
8. Export (PDF)

### Should Have (Phase 8-9)
9. ATS Analysis
10. AI Improvements
11. Complete Frontend UI
12. Multiple Templates

### Nice to Have (Phase 10-12)
13. JD Matching
14. DOCX Export
15. Advanced Analytics
16. Performance Optimizations

## Time Estimates

- Phase 1-2 (Backend Core + Auth): 1 week
- Phase 3 (Parser): 2 weeks
- Phase 4 (Templates): 1.5 weeks
- Phase 5 (ATS): 1 week
- Phase 6 (AI): 1 week
- Phase 7 (Export): 1 week
- Phase 8 (JD Matching): 1 week
- Phase 9 (Frontend): 3 weeks
- Phase 10 (Testing): 1 week
- Phase 11-12 (DevOps + Production): 1 week

**Total: ~13-14 weeks for complete production-ready system**

## Next Immediate Actions

1. Create database models (SQLAlchemy)
2. Setup Alembic migrations
3. Create FastAPI application entry point
4. Implement health check endpoint
5. Setup Docker Compose for local development
6. Implement authentication endpoints
7. Start parser implementation

## Code Quality Standards

- All code must follow Clean Architecture principles
- SOLID principles enforced
- Type hints mandatory (Python) / TypeScript (Frontend)
- Unit tests for business logic (>80% coverage)
- Integration tests for API endpoints
- E2E tests for critical user flows
- Code review before merge
- Documentation for complex logic
