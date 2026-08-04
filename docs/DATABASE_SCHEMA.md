# URCV Database Schema

## Core Tables

### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

### resumes
```sql
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'Untitled Resume',
    original_filename VARCHAR(500),
    original_file_url TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    -- Status: uploaded, parsing, parsed, verified, ready
    
    -- Resume JSON (source of truth)
    resume_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Parser metadata
    parser_version VARCHAR(50),
    parsed_at TIMESTAMP,
    confidence_scores JSONB DEFAULT '{}'::jsonb,
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verification_mode VARCHAR(50),
    -- Mode: perfect, verified, assisted, safe_layout
    
    -- ATS
    ats_score INTEGER,
    ats_analysis JSONB DEFAULT '{}'::jsonb,
    last_ats_check_at TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN ('uploaded', 'parsing', 'parsed', 'verification_needed', 'verified', 'ready', 'error')),
    CONSTRAINT valid_mode CHECK (verification_mode IS NULL OR verification_mode IN ('perfect', 'verified', 'assisted', 'safe_layout'))
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_status ON resumes(status);
CREATE INDEX idx_resumes_created_at ON resumes(created_at DESC);
CREATE INDEX idx_resumes_deleted_at ON resumes(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_resumes_data_gin ON resumes USING gin(resume_data);
```

### templates
```sql
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    -- Category: college, company, generic, ats
    
    description TEXT,
    thumbnail_url TEXT,
    preview_url TEXT,
    
    -- Template definition
    template_schema JSONB NOT NULL,
    -- Defines required fields, optional fields, layout rules
    
    layout_config JSONB NOT NULL,
    -- Font, margins, spacing, sections order
    
    style_config JSONB NOT NULL,
    -- Colors, typography, borders
    
    -- Template metadata
    institution VARCHAR(255),
    -- e.g., "Amity University", "MIT", "Generic"
    
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_templates_slug ON templates(slug);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_institution ON templates(institution);
CREATE INDEX idx_templates_is_active ON templates(is_active) WHERE is_active = TRUE;
```

### exports
```sql
CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    template_id UUID REFERENCES templates(id),
    
    export_type VARCHAR(50) NOT NULL,
    -- Type: pdf, docx, ats_pdf, template_pdf
    
    file_url TEXT NOT NULL,
    file_size_bytes INTEGER,
    
    -- Export settings used
    settings JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exports_resume_id ON exports(resume_id);
CREATE INDEX idx_exports_created_at ON exports(created_at DESC);
```

### job_descriptions
```sql
CREATE TABLE job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    title VARCHAR(500) NOT NULL,
    company VARCHAR(255),
    description TEXT NOT NULL,
    
    -- Parsed JD data
    required_skills TEXT[],
    preferred_skills TEXT[],
    keywords TEXT[],
    extracted_data JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jd_user_id ON job_descriptions(user_id);
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at DESC);
```

### jd_matches
```sql
CREATE TABLE jd_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    jd_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    
    match_score DECIMAL(5,2) NOT NULL,
    -- 0.00 to 100.00
    
    analysis JSONB NOT NULL,
    -- {
    --   "missing_skills": [],
    --   "matched_skills": [],
    --   "missing_keywords": [],
    --   "recommendations": []
    -- }
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(resume_id, jd_id)
);

CREATE INDEX idx_jd_matches_resume_id ON jd_matches(resume_id);
CREATE INDEX idx_jd_matches_jd_id ON jd_matches(jd_id);
```

### ai_improvements
```sql
CREATE TABLE ai_improvements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    section_type VARCHAR(100) NOT NULL,
    -- project, experience, summary, achievement
    
    section_index INTEGER,
    -- Which item in the array (for projects[2], this would be 2)
    
    original_content TEXT NOT NULL,
    improved_content TEXT NOT NULL,
    
    improvement_type VARCHAR(50) NOT NULL,
    -- grammar, action_verbs, professional_tone, clarity
    
    is_applied BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMP,
    
    ai_model VARCHAR(100),
    ai_prompt_version VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ai_improvements_resume_id ON ai_improvements(resume_id);
CREATE INDEX idx_ai_improvements_user_id ON ai_improvements(user_id);
```

### verification_sessions
```sql
CREATE TABLE verification_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    
    sections_to_verify TEXT[] NOT NULL,
    -- ["personal", "projects", "experience"]
    
    verified_sections JSONB DEFAULT '[]'::jsonb,
    -- [{"section": "personal", "verified_at": "...", "method": "tap"}]
    
    status VARCHAR(50) DEFAULT 'pending',
    -- pending, in_progress, completed
    
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_verification_resume_id ON verification_sessions(resume_id);
```

### refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    revoked_at TIMESTAMP
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

### audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    -- upload_resume, parse_resume, export_pdf, etc.
    
    resource_type VARCHAR(50),
    resource_id UUID,
    
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

## Indexes for Performance

```sql
-- GIN indexes for JSONB searches
CREATE INDEX idx_resumes_personal_info ON resumes USING gin((resume_data->'personal'));
CREATE INDEX idx_resumes_skills ON resumes USING gin((resume_data->'skills'));

-- Full-text search
CREATE INDEX idx_resumes_fulltext ON resumes USING gin(to_tsvector('english', 
    COALESCE(resume_data->>'summary', '') || ' ' ||
    COALESCE((resume_data->>'skills')::text, '')
));
```

## Views

```sql
-- Active resumes with user info
CREATE VIEW active_resumes_with_users AS
SELECT 
    r.*,
    u.email,
    u.full_name as user_name
FROM resumes r
JOIN users u ON r.user_id = u.id
WHERE r.deleted_at IS NULL
    AND u.is_active = TRUE;

-- Resume statistics per user
CREATE VIEW user_resume_stats AS
SELECT 
    user_id,
    COUNT(*) as total_resumes,
    COUNT(*) FILTER (WHERE is_verified = TRUE) as verified_resumes,
    AVG(ats_score) as avg_ats_score,
    MAX(created_at) as last_resume_created
FROM resumes
WHERE deleted_at IS NULL
GROUP BY user_id;
```
