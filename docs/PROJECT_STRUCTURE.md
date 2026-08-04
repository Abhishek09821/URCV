# URCV Project Structure

## Complete Folder Organization

```
urcv/
├── frontend/                    # React + TypeScript Frontend
│   ├── public/                 # Static assets
│   │   ├── favicon.ico
│   │   └── robots.txt
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── dropdown.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   └── ...
│   │   │   ├── layout/        # Layout components
│   │   │   │   ├── AppLayout.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Footer.tsx
│   │   │   │   └── MobileNav.tsx
│   │   │   ├── forms/         # Form components
│   │   │   │   ├── FormField.tsx
│   │   │   │   ├── FormSection.tsx
│   │   │   │   ├── FileUpload.tsx
│   │   │   │   └── DatePicker.tsx
│   │   │   └── shared/        # Shared components
│   │   │       ├── Loading.tsx
│   │   │       ├── ErrorBoundary.tsx
│   │   │       ├── ConfidenceBadge.tsx
│   │   │       └── EmptyState.tsx
│   │   ├── features/          # Feature modules
│   │   │   ├── auth/
│   │   │   │   ├── components/
│   │   │   │   │   ├── LoginForm.tsx
│   │   │   │   │   ├── RegisterForm.tsx
│   │   │   │   │   └── ForgotPassword.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   ├── useAuth.ts
│   │   │   │   │   └── useLogin.ts
│   │   │   │   ├── services/
│   │   │   │   │   └── authService.ts
│   │   │   │   ├── types/
│   │   │   │   │   └── auth.types.ts
│   │   │   │   └── routes/
│   │   │   │       ├── LoginPage.tsx
│   │   │   │       └── RegisterPage.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── components/
│   │   │   │   │   ├── DashboardStats.tsx
│   │   │   │   │   ├── RecentResumes.tsx
│   │   │   │   │   └── QuickActions.tsx
│   │   │   │   └── routes/
│   │   │   │       └── DashboardPage.tsx
│   │   │   ├── resume/
│   │   │   │   ├── components/
│   │   │   │   │   ├── ResumeUpload.tsx
│   │   │   │   │   ├── ResumeEditor/
│   │   │   │   │   │   ├── index.tsx
│   │   │   │   │   │   ├── PersonalSection.tsx
│   │   │   │   │   │   ├── EducationSection.tsx
│   │   │   │   │   │   ├── ProjectSection.tsx
│   │   │   │   │   │   ├── ExperienceSection.tsx
│   │   │   │   │   │   ├── SkillsSection.tsx
│   │   │   │   │   │   └── CertificationSection.tsx
│   │   │   │   │   ├── ResumePreview.tsx
│   │   │   │   │   ├── VerificationUI.tsx
│   │   │   │   │   └── ParsingProgress.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   ├── useResumeUpload.ts
│   │   │   │   │   ├── useResumeParser.ts
│   │   │   │   │   └── useResumeEditor.ts
│   │   │   │   ├── services/
│   │   │   │   │   └── resumeService.ts
│   │   │   │   └── routes/
│   │   │   │       ├── ResumeListPage.tsx
│   │   │   │       ├── ResumeUploadPage.tsx
│   │   │   │       └── ResumeEditorPage.tsx
│   │   │   ├── template/
│   │   │   │   ├── components/
│   │   │   │   │   ├── TemplateGallery.tsx
│   │   │   │   │   ├── TemplateCard.tsx
│   │   │   │   │   ├── TemplatePreview.tsx
│   │   │   │   │   ├── TemplateConverter.tsx
│   │   │   │   │   └── OverflowWarning.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useTemplateConversion.ts
│   │   │   │   ├── services/
│   │   │   │   │   └── templateService.ts
│   │   │   │   └── routes/
│   │   │   │       └── TemplateConverterPage.tsx
│   │   │   ├── ats/
│   │   │   │   ├── components/
│   │   │   │   │   ├── ATSScoreCard.tsx
│   │   │   │   │   ├── ATSBreakdown.tsx
│   │   │   │   │   ├── ATSSuggestions.tsx
│   │   │   │   │   └── ATSProgress.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useATSAnalysis.ts
│   │   │   │   ├── services/
│   │   │   │   │   └── atsService.ts
│   │   │   │   └── routes/
│   │   │   │       └── ATSAnalysisPage.tsx
│   │   │   ├── export/
│   │   │   │   ├── components/
│   │   │   │   │   ├── ExportOptions.tsx
│   │   │   │   │   ├── FormatSelector.tsx
│   │   │   │   │   └── ExportHistory.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useExport.ts
│   │   │   │   └── services/
│   │   │   │       └── exportService.ts
│   │   │   └── settings/
│   │   │       ├── components/
│   │   │       │   ├── ProfileSettings.tsx
│   │   │       │   ├── SecuritySettings.tsx
│   │   │       │   └── PreferencesSettings.tsx
│   │   │       └── routes/
│   │   │           └── SettingsPage.tsx
│   │   ├── hooks/             # Global hooks
│   │   │   ├── useDebounce.ts
│   │   │   ├── useLocalStorage.ts
│   │   │   ├── useMediaQuery.ts
│   │   │   └── useToast.ts
│   │   ├── lib/               # Library configurations
│   │   │   ├── axios.ts
│   │   │   ├── queryClient.ts
│   │   │   └── utils.ts
│   │   ├── services/          # Global services
│   │   │   ├── api.ts
│   │   │   └── storage.ts
│   │   ├── store/             # Global state (Zustand)
│   │   │   ├── authStore.ts
│   │   │   ├── uiStore.ts
│   │   │   └── index.ts
│   │   ├── types/             # Global TypeScript types
│   │   │   ├── resume.types.ts
│   │   │   ├── template.types.ts
│   │   │   ├── api.types.ts
│   │   │   └── index.ts
│   │   ├── utils/             # Utility functions
│   │   │   ├── validation.ts
│   │   │   ├── formatting.ts
│   │   │   ├── date.ts
│   │   │   └── constants.ts
│   │   ├── styles/            # Global styles
│   │   │   ├── globals.css
│   │   │   └── variables.css
│   │   ├── App.tsx            # Root component
│   │   ├── main.tsx           # Entry point
│   │   └── vite-env.d.ts      # Vite types
│   ├── .env.example
│   ├── .env.local
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── api/               # API layer
│   │   │   ├── routes/        # Route handlers
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── resume.py
│   │   │   │   ├── template.py
│   │   │   │   ├── ats.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── export.py
│   │   │   │   ├── jd.py
│   │   │   │   └── health.py
│   │   │   ├── dependencies/   # Dependency injection
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── database.py
│   │   │   │   └── services.py
│   │   │   └── middlewares/    # Custom middlewares
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── error_handler.py
│   │   │       ├── logging.py
│   │   │       └── rate_limit.py
│   │   ├── core/              # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py      # Settings management
│   │   │   ├── security.py    # Security utilities
│   │   │   ├── logging.py     # Logging config
│   │   │   └── exceptions.py  # Custom exceptions
│   │   ├── domain/            # Domain models (Business logic)
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── resume.py
│   │   │   │   ├── template.py
│   │   │   │   └── export.py
│   │   │   ├── schemas/       # Resume JSON schema
│   │   │   │   ├── __init__.py
│   │   │   │   ├── resume_schema.py
│   │   │   │   └── validators.py
│   │   │   └── rules/         # Business rules
│   │   │       ├── __init__.py
│   │   │       ├── ats_rules.py
│   │   │       ├── layout_rules.py
│   │   │       └── validation_rules.py
│   │   ├── infrastructure/    # External services
│   │   │   ├── __init__.py
│   │   │   ├── database/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── session.py
│   │   │   │   └── models.py  # SQLAlchemy models
│   │   │   ├── storage/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── s3.py
│   │   │   │   └── local.py
│   │   │   ├── cache/
│   │   │   │   ├── __init__.py
│   │   │   │   └── redis.py
│   │   │   ├── ai_client/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── claude.py
│   │   │   │   ├── gemini.py
│   │   │   │   └── base.py
│   │   │   └── pdf_processor/
│   │   │       ├── __init__.py
│   │   │       ├── extractor.py
│   │   │       ├── ocr.py
│   │   │       └── generator.py
│   │   ├── features/          # Feature modules
│   │   │   ├── __init__.py
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── utils.py
│   │   │   ├── resume/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   ├── parser/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── pipeline.py
│   │   │   │   │   ├── extractors/
│   │   │   │   │   │   ├── text_extractor.py
│   │   │   │   │   │   ├── ocr_extractor.py
│   │   │   │   │   │   └── ai_extractor.py
│   │   │   │   │   ├── rules/
│   │   │   │   │   │   ├── email_rule.py
│   │   │   │   │   │   ├── phone_rule.py
│   │   │   │   │   │   ├── date_rule.py
│   │   │   │   │   │   └── section_rule.py
│   │   │   │   │   ├── confidence.py
│   │   │   │   │   └── normalizer.py
│   │   │   │   ├── schemas.py
│   │   │   │   └── tasks.py   # Celery tasks
│   │   │   ├── template/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   ├── engine/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── converter.py
│   │   │   │   │   ├── mapper.py
│   │   │   │   │   ├── layout_calculator.py
│   │   │   │   │   ├── overflow_detector.py
│   │   │   │   │   └── renderer.py
│   │   │   │   ├── templates/  # Template definitions
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base.py
│   │   │   │   │   ├── amity.py
│   │   │   │   │   ├── generic.py
│   │   │   │   │   └── ats_optimized.py
│   │   │   │   └── schemas.py
│   │   │   ├── ats/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   ├── engine/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── analyzer.py
│   │   │   │   │   ├── checks/
│   │   │   │   │   │   ├── contact_check.py
│   │   │   │   │   │   ├── section_check.py
│   │   │   │   │   │   ├── formatting_check.py
│   │   │   │   │   │   ├── keyword_check.py
│   │   │   │   │   │   └── readability_check.py
│   │   │   │   │   └── scorer.py
│   │   │   │   └── schemas.py
│   │   │   ├── ai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   ├── improver/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── project_improver.py
│   │   │   │   │   ├── experience_improver.py
│   │   │   │   │   ├── summary_improver.py
│   │   │   │   │   └── prompts.py
│   │   │   │   ├── jd_matcher.py
│   │   │   │   └── schemas.py
│   │   │   ├── export/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── service.py
│   │   │   │   ├── generators/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── pdf_generator.py
│   │   │   │   │   ├── docx_generator.py
│   │   │   │   │   └── ats_pdf_generator.py
│   │   │   │   └── schemas.py
│   │   │   └── jd_matching/
│   │   │       ├── __init__.py
│   │   │       ├── service.py
│   │   │       ├── matcher.py
│   │   │       └── schemas.py
│   │   ├── schemas/           # Pydantic schemas (API contracts)
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── auth.py
│   │   │   ├── resume.py
│   │   │   ├── template.py
│   │   │   └── response.py
│   │   ├── services/          # Shared services
│   │   │   ├── __init__.py
│   │   │   ├── email.py
│   │   │   ├── notification.py
│   │   │   └── analytics.py
│   │   ├── utils/             # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── date.py
│   │   │   ├── text.py
│   │   │   ├── file.py
│   │   │   └── validators.py
│   │   ├── __init__.py
│   │   └── main.py            # FastAPI app entry
│   ├── alembic/               # Database migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py        # Pytest fixtures
│   │   ├── unit/              # Unit tests
│   │   │   ├── test_parser.py
│   │   │   ├── test_ats.py
│   │   │   └── test_template.py
│   │   ├── integration/       # Integration tests
│   │   │   ├── test_api.py
│   │   │   └── test_pipeline.py
│   │   └── e2e/               # End-to-end tests
│   │       └── test_user_flow.py
│   ├── scripts/               # Utility scripts
│   │   ├── seed_templates.py
│   │   └── init_db.py
│   ├── .env.example
│   ├── .env
│   ├── .python-version
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── README.md
│
├── shared/                     # Shared between frontend/backend
│   ├── types/
│   │   └── resume.types.ts
│   └── constants/
│       └── common.ts
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        ✓ Created
│   ├── DATABASE_SCHEMA.md     ✓ Created
│   ├── RESUME_JSON_SCHEMA.md  ✓ Created
│   ├── PROJECT_STRUCTURE.md   → Current file
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
│
├── design-system/              # Design tokens & guidelines
│   ├── colors.json
│   ├── typography.json
│   └── spacing.json
│
├── templates/                  # Resume template definitions
│   ├── amity/
│   │   ├── config.json
│   │   ├── preview.png
│   │   └── template.html
│   ├── generic/
│   │   ├── config.json
│   │   ├── preview.png
│   │   └── template.html
│   └── ats-optimized/
│       ├── config.json
│       ├── preview.png
│       └── template.html
│
├── tests/                      # E2E tests
│   └── playwright/
│       ├── auth.spec.ts
│       ├── resume.spec.ts
│       └── template.spec.ts
│
├── .github/                    # GitHub Actions
│   └── workflows/
│       ├── frontend-ci.yml
│       ├── backend-ci.yml
│       └── deploy.yml
│
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production
├── .gitignore
├── .prettierrc
├── .editorconfig
├── LICENSE
├── DECISIONS.md               ✓ Read
├── Future.md                  ✓ Read
├── PRD.md                     ✓ Read
└── README.md
```

## Key Architectural Decisions

### Frontend Architecture
1. **Feature-Based Structure**: Each feature is self-contained with its components, hooks, services, and types
2. **Atomic Design**: UI components organized by complexity (ui → shared → feature components)
3. **Co-location**: Keep related code together (component + styles + tests)
4. **Lazy Loading**: Route-based code splitting for performance

### Backend Architecture
1. **Clean Architecture**: Clear separation of concerns across layers
2. **Dependency Injection**: Services injected via FastAPI dependencies
3. **Feature Modules**: Each feature has service, schemas, and business logic
4. **Async First**: Leverage async/await for I/O operations
5. **Type Safety**: Pydantic for runtime validation

### Database Strategy
1. **Resume JSON in JSONB**: Source of truth stored in PostgreSQL
2. **Proper Indexing**: GIN indexes for JSONB queries
3. **Migrations**: Alembic for version control
4. **Soft Deletes**: Keep deleted_at for recovery

### File Organization Principles
1. **Single Responsibility**: Each file has one clear purpose
2. **Import Hierarchy**: Components import from lib/utils, not vice versa
3. **No Circular Dependencies**: Strict import order
4. **Index Files**: Barrel exports for clean imports

## File Naming Conventions

```
Frontend:
- Components: PascalCase (UserProfile.tsx)
- Hooks: camelCase with use prefix (useAuth.ts)
- Utils: camelCase (formatDate.ts)
- Types: camelCase with .types suffix (resume.types.ts)
- Services: camelCase with Service suffix (authService.ts)

Backend:
- Modules: snake_case (user_service.py)
- Classes: PascalCase (UserService)
- Functions: snake_case (parse_resume)
- Constants: UPPER_SNAKE_CASE (MAX_FILE_SIZE)
- Tests: test_ prefix (test_parser.py)
```

## Import Order

```typescript
// Frontend
1. External libraries (react, react-router, etc.)
2. Internal libraries (@/lib/*)
3. Components (@/components/*)
4. Features (@/features/*)
5. Hooks (@/hooks/*)
6. Types (@/types/*)
7. Utils (@/utils/*)
8. Relative imports (./...)

// Backend
1. Standard library
2. Third-party packages
3. FastAPI imports
4. Local app imports (app.*)
5. Relative imports (.)
```

## Testing Structure

```
tests/
├── unit/              # Isolated function tests
├── integration/       # Multiple modules together
└── e2e/              # Full user workflows

Each test file mirrors source structure:
src/features/resume/parser.py → tests/unit/test_resume_parser.py
```

This structure supports:
- Clean Architecture
- SOLID principles
- Feature-based development
- Easy testing
- Clear responsibilities
- Scalability
