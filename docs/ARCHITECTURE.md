# URCV System Architecture

## Overview

URCV is a production-grade SaaS platform built with Clean Architecture principles, Feature-Based organization, and mobile-first design.

## Architecture Principles

### 1. Clean Architecture
- **Independence**: Business logic independent of frameworks
- **Testability**: Core logic testable without UI/DB
- **Separation**: Clear boundaries between layers
- **Dependency Rule**: Dependencies point inward only

### 2. SOLID Principles
- **Single Responsibility**: Each module has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Clients shouldn't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

### 3. Feature-Based Organization
- Features are self-contained modules
- Each feature has its own: routes, components, services, types
- Shared code lives in common modules

## System Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                   │
│                                                          │
│  React Components (Mobile-First)                        │
│  - Pages (route components)                             │
│  - Feature Components                                   │
│  - Shared UI Components (Design System)                 │
│  - Forms with validation                                │
│                                                          │
│  State Management: TanStack Query + Zustand             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP/REST API
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Application Layer                      │
│                                                          │
│  Use Cases / Business Logic                             │
│  - Resume Upload & Parsing                              │
│  - Template Conversion                                  │
│  - ATS Analysis                                         │
│  - AI Improvements                                      │
│  - Export Generation                                    │
│                                                          │
│  Services: Authentication, Authorization, Validation    │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Domain Models
                     │
┌────────────────────▼────────────────────────────────────┐
│                     Domain Layer                        │
│                                                          │
│  Core Business Entities                                 │
│  - Resume JSON Schema                                   │
│  - Template Schema                                      │
│  - ATS Rules Engine                                     │
│  - Business Rules & Validation                          │
│                                                          │
│  No external dependencies                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Interfaces
                     │
┌────────────────────▼────────────────────────────────────┐
│                Infrastructure Layer                     │
│                                                          │
│  External Services & Adapters                           │
│  - FastAPI Framework                                    │
│  - PostgreSQL Database (SQLAlchemy)                     │
│  - S3 Storage (boto3)                                   │
│  - Redis Cache                                          │
│  - PDF Processing (PyMuPDF, pdfplumber)                 │
│  - AI Services (Claude API, Gemini)                     │
│  - Email Service                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Core Pipelines

### 1. Resume Upload & Parsing Pipeline

```
User Uploads PDF
      │
      ▼
Frontend Validation
- File type check (PDF only)
- File size check (< 10MB)
- Basic PDF structure
      │
      ▼
Upload to S3
- Generate unique file ID
- Store in /uploads/{user_id}/original/
- Return signed URL
      │
      ▼
Create Resume Record
- Status: "uploaded"
- Store file metadata
      │
      ▼
Trigger Async Parse Job
(Celery Task)
      │
      ▼
┌─────────────────────────────────────┐
│      Resume Parser Pipeline         │
│                                     │
│  1. PDF Extraction                  │
│     - PyMuPDF (text + structure)    │
│     - pdfplumber (tables)           │
│     - Layout detection              │
│                                     │
│  2. OCR Fallback (if needed)        │
│     - pytesseract                   │
│     - Image-based PDF detection     │
│                                     │
│  3. Rule-Based Extraction           │
│     - Regex patterns for email,     │
│       phone, dates                  │
│     - Section detection             │
│     - Bullet point extraction       │
│                                     │
│  4. AI-Enhanced Extraction          │
│     - Claude API for ambiguous      │
│       content                       │
│     - Entity recognition            │
│     - Context understanding         │
│                                     │
│  5. Confidence Scoring              │
│     - Per-field confidence          │
│     - Per-section confidence        │
│     - Overall confidence            │
│                                     │
│  6. Resume JSON Generation          │
│     - Validate against schema       │
│     - Normalize data                │
│     - Generate UUIDs                │
│                                     │
└─────────────┬───────────────────────┘
              │
              ▼
Update Resume Record
- Status: "parsed"
- Store Resume JSON
- Store confidence scores
              │
              ▼
Verification Check
- If confidence < 85% → "verification_needed"
- If confidence >= 85% → "ready"
              │
              ▼
Notify Frontend
- WebSocket/SSE update
- Show verification UI if needed
```

### 2. Template Conversion Pipeline

```
User Selects Template
      │
      ▼
Load Resume JSON + Template Schema
      │
      ▼
┌─────────────────────────────────────┐
│   Universal Template Engine         │
│                                     │
│  1. Field Mapping                   │
│     - Map Resume JSON to template   │
│     - Handle missing fields         │
│     - Handle custom fields          │
│                                     │
│  2. Layout Calculation              │
│     - Measure content size          │
│     - Check overflow                │
│     - Calculate spacing             │
│                                     │
│  3. Overflow Detection              │
│     - Warn if content exceeds       │
│     - Suggest compression           │
│     - Never silently truncate       │
│                                     │
│  4. Style Application               │
│     - Apply template fonts          │
│     - Apply colors                  │
│     - Apply margins/spacing         │
│                                     │
│  5. Render                          │
│     - Generate HTML                 │
│     - Convert to PDF (WeasyPrint)   │
│     - Preserve layout rules         │
│                                     │
└─────────────┬───────────────────────┘
              │
              ▼
Preview Generation
- Store preview in S3
- Return URL to frontend
              │
              ▼
User Reviews Preview
- Accept → Generate final export
- Reject → Adjust content
```

### 3. ATS Analysis Pipeline

```
User Requests ATS Check
      │
      ▼
Load Resume JSON
      │
      ▼
┌─────────────────────────────────────┐
│        ATS Analysis Engine          │
│                                     │
│  1. Contact Information (15%)       │
│     ✓ Email present                 │
│     ✓ Phone present                 │
│     ✓ Valid formats                 │
│                                     │
│  2. Section Structure (20%)         │
│     ✓ Education present             │
│     ✓ Experience/Projects present   │
│     ✓ Skills present                │
│     ✓ Proper section ordering       │
│                                     │
│  3. Formatting (25%)                │
│     ✓ No tables/columns             │
│     ✓ Standard fonts                │
│     ✓ No headers/footers            │
│     ✓ No images/graphics            │
│     ✓ Proper date formats           │
│                                     │
│  4. Keywords (20%)                  │
│     ✓ Technical skills mentioned    │
│     ✓ Action verbs present          │
│     ✓ Industry terms                │
│                                     │
│  5. Readability (10%)               │
│     ✓ Bullet points used            │
│     ✓ Concise descriptions          │
│     ✓ No spelling errors            │
│                                     │
│  6. File Structure (10%)            │
│     ✓ Single page preferred         │
│     ✓ PDF format                    │
│     ✓ No password protection        │
│                                     │
└─────────────┬───────────────────────┘
              │
              ▼
Generate ATS Report
- Overall score (0-100)
- Per-category scores
- Specific suggestions
- Priority fixes
              │
              ▼
Store Analysis
- Cache for 24 hours
- Update resume record
              │
              ▼
Return to Frontend
- Show score breakdown
- Show actionable suggestions
```

### 4. AI Improvement Pipeline

```
User Selects Section to Improve
(e.g., Project #2)
      │
      ▼
Extract Original Content
      │
      ▼
┌─────────────────────────────────────┐
│      AI Improvement Engine          │
│                                     │
│  1. Context Preparation             │
│     - Section type                  │
│     - Original content              │
│     - Improvement type requested    │
│                                     │
│  2. Prompt Construction             │
│     - System prompt (maintain tone) │
│     - User context                  │
│     - Specific instructions         │
│                                     │
│  3. AI Call (Claude 3.5 Sonnet)     │
│     - Temperature: 0.7              │
│     - Max tokens: 500               │
│     - Streaming response            │
│                                     │
│  4. Response Validation             │
│     - Check for hallucinations      │
│     - Verify fact preservation      │
│     - Length check                  │
│                                     │
│  5. Store Suggestion                │
│     - Original + improved           │
│     - Don't auto-apply              │
│     - User must review              │
│                                     │
└─────────────┬───────────────────────┘
              │
              ▼
Present to User
- Side-by-side comparison
- Highlight changes
- Accept / Reject / Regenerate
              │
              ▼
If Accepted
- Update Resume JSON
- Mark as modified by AI
- Update lastModified timestamp
```

## Technology Stack Details

### Frontend Stack

```typescript
// Core
React 18.2+              // UI library
TypeScript 5.0+          // Type safety
Vite 5.0+               // Build tool, super fast HMR

// UI & Styling
Tailwind CSS 3.4+       // Utility-first CSS
shadcn/ui               // Accessible components
Radix UI                // Headless components
Lucide React            // Icons
class-variance-authority // Component variants

// Forms & Validation
React Hook Form 7.0+    // Form state management
Zod 3.0+               // Schema validation
@hookform/resolvers     // Bridge RHF + Zod

// State & Data
TanStack Query 5.0+     // Server state
Zustand 4.0+           // Client state (lightweight)
Axios 1.6+             // HTTP client
Immer                  // Immutable state updates

// Routing
React Router 6.0+      // Client-side routing

// PDF
react-pdf 7.0+         // PDF preview
pdf-lib                // PDF manipulation

// Utilities
date-fns               // Date manipulation
lodash-es              // Utility functions
nanoid                 // ID generation
clsx / cn              // Conditional classes
```

### Backend Stack

```python
# Core
fastapi==0.108.0+           # Web framework
uvicorn[standard]==0.25.0+  # ASGI server
python==3.11+               # Python version

# Database
sqlalchemy==2.0+            # ORM
alembic==1.13.0+           # Migrations
asyncpg==0.29.0+           # Async PostgreSQL driver
psycopg2-binary==2.9+      # Sync PostgreSQL driver

# Validation
pydantic==2.5+             # Data validation
pydantic-settings==2.1+    # Settings management
email-validator==2.1+      # Email validation

# Authentication
python-jose[cryptography]  # JWT
passlib[bcrypt]           # Password hashing
python-multipart          # Form data

# PDF Processing
PyMuPDF==1.23.0+          # PDF extraction (fitz)
pdfplumber==0.10.0+       # PDF tables
pytesseract==0.3.10+      # OCR
Pillow==10.1.0+           # Image processing
reportlab==4.0+           # PDF generation
weasyprint==60.0+         # HTML to PDF

# AI
anthropic==0.8.0+         # Claude API
google-generativeai==0.3+ # Gemini API
langchain==0.1.0+         # LLM orchestration
langchain-anthropic       # Anthropic integration

# Storage
boto3==1.34.0+            # AWS S3
python-magic==0.4.27+     # File type detection

# Task Queue
celery==5.3.0+            # Async tasks
redis==5.0.0+             # Message broker

# Caching
redis==5.0.0+             # Cache layer
hiredis==2.2.0+          # Fast Redis client

# Monitoring
sentry-sdk==1.39.0+       # Error tracking
python-json-logger==2.0+  # Structured logging

# Testing
pytest==7.4.0+            # Test framework
pytest-asyncio==0.21.0+   # Async tests
pytest-cov==4.1.0+        # Coverage
httpx==0.25.0+            # Async HTTP client for tests
faker==20.0.0+            # Fake data generation

# Development
black==23.12.0+           # Code formatter
ruff==0.1.0+              # Linter
mypy==1.7.0+              # Type checker
pre-commit==3.6.0+        # Git hooks

# Rate Limiting
slowapi==0.1.9+           # Rate limiting

# CORS
fastapi-cors              # CORS middleware
```

### Database & Infrastructure

```yaml
PostgreSQL: 15+
  Extensions:
    - uuid-ossp          # UUID generation
    - pgcrypto           # Encryption
    - pg_trgm            # Fuzzy search
    - btree_gin          # Multi-column indexes
    
Redis: 7+
  Use Cases:
    - Session storage
    - Cache layer
    - Celery broker
    - Rate limiting
    
S3-Compatible Storage:
  - AWS S3 (production)
  - MinIO (local development)
  Structure:
    - urcv-uploads/{user_id}/original/
    - urcv-uploads/{user_id}/processed/
    - urcv-exports/{user_id}/{export_id}/
    - urcv-templates/
```

## Security Architecture

### Authentication Flow

```
1. User Registration
   - Email + Password
   - Hash password (bcrypt, cost=12)
   - Create user record
   - Send verification email

2. User Login
   - Validate credentials
   - Generate JWT access token (15 min expiry)
   - Generate refresh token (7 days expiry)
   - Store refresh token hash in DB
   - Return both tokens

3. Token Refresh
   - Validate refresh token
   - Check if revoked
   - Generate new access token
   - Optionally rotate refresh token

4. Logout
   - Revoke refresh token
   - Blacklist access token (Redis)
```

### Authorization

```
Role-Based Access Control (RBAC)

Roles:
  - user: Basic access
  - premium: Advanced features
  - admin: Full access

Permissions checked at:
  - API route level (decorators)
  - Service level (explicit checks)
  - Database level (row-level security)
```

### Security Measures

```yaml
API Security:
  - Rate limiting (per IP, per user)
  - CORS (whitelist only)
  - CSRF protection
  - Input validation (Pydantic)
  - SQL injection prevention (ORM)
  - XSS prevention (output escaping)

File Security:
  - File type validation (magic bytes)
  - File size limits (10MB for PDFs)
  - Virus scanning (ClamAV)
  - Signed URLs (expiring)
  - Private buckets (no public access)

Data Security:
  - Encryption at rest (S3, PostgreSQL)
  - Encryption in transit (TLS 1.3)
  - Sensitive data hashing
  - PII masking in logs
  - Regular backups

Monitoring:
  - Error tracking (Sentry)
  - Audit logs (all user actions)
  - Security headers (helmet equivalent)
  - DDoS protection (Cloudflare)
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cloudflare CDN                       │
│                  (DDoS, SSL, Caching)                   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌───────────────┐
│   Vercel      │         │   Railway     │
│  (Frontend)   │◄───────►│  (Backend)    │
│               │   API   │               │
│ - React SPA   │         │ - FastAPI     │
│ - CDN Edge    │         │ - Uvicorn     │
│ - Auto-scale  │         │ - Workers     │
└───────────────┘         └───────┬───────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │PostgreSQL│  │  Redis   │  │   S3     │
            │ (Neon)   │  │(Railway) │  │  (AWS)   │
            └──────────┘  └──────────┘  └──────────┘
```

### Environment Strategy

```
Development:
  - Local Docker Compose
  - Hot reload enabled
  - Debug mode on
  - MinIO for S3
  - Local PostgreSQL/Redis

Staging:
  - Replica of production
  - Test data seeded
  - Monitoring enabled
  - Separate API keys

Production:
  - Auto-scaling enabled
  - Zero-downtime deploys
  - Database replication
  - Automated backups
  - Real monitoring
```

## Performance Optimizations

### Frontend
- Code splitting (route-based)
- Lazy loading components
- Image optimization (next/image)
- Bundle size monitoring
- Service worker caching
- Virtual scrolling (large lists)

### Backend
- Database connection pooling
- Redis caching (frequent queries)
- Async operations (I/O bound)
- Background jobs (Celery)
- Query optimization (indexes)
- Response compression (gzip)

### Database
- Proper indexing strategy
- Query result caching
- Connection pooling
- JSONB indexes for Resume JSON
- Partitioning (audit_logs by date)

## Monitoring & Observability

```yaml
Logging:
  - Structured JSON logs
  - Log levels (INFO, WARN, ERROR)
  - Request/response logging
  - Performance metrics
  
Metrics:
  - API response times
  - Database query times
  - Cache hit rates
  - Error rates
  - User activity
  
Alerts:
  - High error rate
  - Slow responses (> 2s)
  - Database connection issues
  - Storage quota warnings
  - Security incidents

Tools:
  - Sentry: Error tracking
  - PostHog: Analytics
  - Railway Metrics: Infrastructure
  - Custom dashboards
```

## Scalability Strategy

### Horizontal Scaling
- Stateless API servers
- Load balancer (automatic)
- Database read replicas
- Distributed cache (Redis cluster)

### Vertical Scaling
- Database resources
- Worker processes
- Memory allocation

### Cost Optimization
- S3 lifecycle policies
- Database query optimization
- Cache effectively
- Compress responses
- Optimize images

## Disaster Recovery

```yaml
Backups:
  Database:
    - Automated daily backups
    - Point-in-time recovery
    - Retention: 30 days
    
  Files:
    - S3 versioning enabled
    - Cross-region replication
    - Retention: 90 days

Recovery Plan:
  RTO: 4 hours  # Recovery Time Objective
  RPO: 1 hour   # Recovery Point Objective
  
  Steps:
    1. Detect incident
    2. Assess impact
    3. Restore from backup
    4. Verify data integrity
    5. Resume operations
    6. Post-mortem
```

This architecture is production-ready, scalable, secure, and maintainable. It follows industry best practices and can handle thousands of concurrent users.
