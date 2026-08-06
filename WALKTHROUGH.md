# URCV Complete Application Walkthrough

This document provides a complete walkthrough of the URCV application, showing how every feature works and how it all connects together.

---

## Table of Contents

1. [Application Start](#application-start)
2. [User Registration](#user-registration)
3. [User Login](#user-login)
4. [Dashboard](#dashboard)
5. [Resume Upload](#resume-upload)
6. [Resume Detail & Editor](#resume-detail--editor)
7. [ATS Analysis](#ats-analysis)
8. [AI Improvements](#ai-improvements)
9. [Export](#export)
10. [Settings](#settings)
11. [Theme Toggle](#theme-toggle)
12. [Logout](#logout)

---

## Application Start

### Step 1: Start Backend Services

```bash
# Terminal 1: Start backend with Docker
cd /Users/abhishektiwari/URCV
docker-compose up -d

# Wait for services (10-15 seconds)
sleep 15

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify backend is healthy
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

**What happens:**
- PostgreSQL starts (database)
- Redis starts (caching)
- MinIO starts (S3-compatible storage)
- Backend API starts (FastAPI)
- Database schema created via migrations

### Step 2: Start Frontend

```bash
# Terminal 2: Start frontend
cd frontend
npm install  # First time only
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

**What happens:**
- Vite dev server starts
- React app compiles
- Opens at http://localhost:3000
- Auto-proxies API calls to backend

### Step 3: Open Application

Open browser: **http://localhost:3000**

**What you see:**
- Login page with email/password fields
- "Sign up" link
- Beautiful gradient background
- Theme toggle icon (top right)

---

## User Registration

### Flow

1. **Click "Sign up" link**
   - Route changes to `/register`
   - RegisterPage component loads

2. **Fill registration form:**
   ```
   Full Name: John Doe
   Email: john@example.com
   Password: password123
   Confirm Password: password123
   ```

3. **Click "Create Account"**

**What happens backend:**
```
Frontend sends POST /api/v1/auth/register
↓
Backend receives request
↓
Validates input (Pydantic)
↓
Checks if email exists
↓
Hashes password (bcrypt, cost 12)
↓
Creates user in database
↓
Returns user object
```

**What happens frontend:**
```
registerMutation executes
↓
On success: Triggers auto-login
↓
Calls POST /api/v1/auth/login
↓
Receives JWT tokens
↓
Stores in localStorage
↓
Sets user in Zustand store
↓
Shows toast "Welcome!"
↓
Navigates to /dashboard
```

**Database changes:**
```sql
INSERT INTO users (email, hashed_password, full_name, ...)
VALUES ('john@example.com', '$2b$12$...', 'John Doe', ...);
```

---

## User Login

### Flow

1. **Enter credentials:**
   ```
   Email: john@example.com
   Password: password123
   ```

2. **Click "Sign In"**

**What happens backend:**
```
POST /api/v1/auth/login
↓
Validate input
↓
Find user by email
↓
Verify password (bcrypt.verify)
↓
Generate access token (JWT, 15 min expiry)
↓
Generate refresh token (JWT, 7 days expiry)
↓
Store refresh token in database
↓
Return tokens
```

**What happens frontend:**
```
loginMutation executes
↓
Receives tokens: {access_token, refresh_token, token_type}
↓
Stores in localStorage under 'urcv_tokens'
↓
Calls GET /api/v1/auth/me to get user details
↓
Stores user in Zustand store
↓
Shows toast "Welcome back!"
↓
Navigates to /dashboard
```

**Token structure:**
```json
{
  "access_token": "eyJhbGc....",  // 15 min
  "refresh_token": "eyJhbGc....", // 7 days
  "token_type": "bearer"
}
```

**Automatic token refresh:**
- Axios interceptor catches 401 errors
- Calls POST /api/v1/auth/refresh with refresh_token
- Gets new tokens
- Retries original request
- User stays logged in seamlessly

---

## Dashboard

### What You See

**Statistics Cards:**
- Total Resumes: 0
- Verified: 0 (0% of total)
- Avg Confidence: 0%
- Need Review: 0

**Recent Resumes:**
- Empty state: "No resumes yet"
- Upload button prominent

### What Happens

```
Component mounts
↓
useResumes hook executes
↓
TanStack Query calls GET /api/v1/resumes?page=1&size=20
↓
Backend queries database
↓
Returns paginated response: {items: [], total: 0, pages: 0}
↓
Frontend displays empty state
```

**Database query:**
```sql
SELECT * FROM resumes 
WHERE user_id = 'current-user-id'
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

---

## Resume Upload

### Flow

1. **Click "Upload Resume"**
   - Navigate to `/upload`
   - UploadPage component loads

2. **Drag & drop PDF file**
   - React Dropzone activates
   - Validates file (PDF, <10MB)
   - Shows file preview

3. **Click "Upload & Parse Resume"**

**What happens backend:**
```
POST /api/v1/resumes/upload (multipart/form-data)
↓
Receive file
↓
Validate file type & size
↓
Generate unique filename
↓
Save PDF to temp location
↓
Extract text (PyMuPDF + pdfplumber)
↓
Run parser pipeline:
  - Extract email (regex)
  - Extract phone (regex)
  - Extract links (regex)
  - Detect sections (rules)
  - Extract skills (keyword matching)
  - Calculate confidence scores
↓
Create Resume JSON
↓
Upload original PDF to S3
↓
Save to database:
  - user_id
  - original_filename
  - file_url (S3)
  - resume_data (JSONB)
  - confidence_score
↓
Return resume object
```

**Parsing example:**
```python
# Input: PDF bytes
# Output: Resume JSON
{
  "personal": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-234-567-8900",
    "location": "San Francisco, CA",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe"
  },
  "summary": "Software engineer with 5 years...",
  "skills": {
    "languages": ["Python", "JavaScript", "Java"],
    "frameworks": ["React", "Django", "Spring"],
    "tools": ["Git", "Docker", "AWS"],
    "databases": ["PostgreSQL", "MongoDB"]
  },
  "experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Software Engineer",
      "start_date": "2020-01",
      "end_date": "2023-12",
      "location": "San Francisco, CA",
      "description": [
        "Led team of 5 engineers",
        "Built microservices architecture",
        "Improved performance by 40%"
      ]
    }
  ],
  "education": [...],
  "projects": [...],
  "certifications": [...]
}
```

**Database storage:**
```sql
INSERT INTO resumes (
  user_id,
  original_filename,
  file_url,
  resume_data,  -- JSONB column
  confidence_score,
  is_verified,
  created_at
) VALUES (
  'user-uuid',
  'resume.pdf',
  's3://bucket/user-uuid/original/resume-uuid.pdf',
  '{"personal": {...}, "summary": "...", ...}',  -- JSON
  87.5,
  false,
  NOW()
);
```

**What happens frontend:**
```
uploadMutation executes
↓
Shows loading state
↓
Receives resume object
↓
Shows toast "Resume uploaded successfully!"
↓
Navigates to /resume/{id}
```

---

## Resume Detail & Editor

### What You See

**Header:**
- Resume name (person's name or filename)
- Upload date
- Verification badge (verified/not verified)
- Confidence score badge (87%)

**Action Buttons:**
- Edit Resume
- Show ATS Analysis
- AI Improvements
- Export
- Mark as Verified (if not verified)
- Delete

**Content:**
- Resume editor with section tabs
- Editable fields (in edit mode)
- View-only display (in view mode)

### Edit Mode Flow

1. **Click "Edit Resume"**
   - `isEditing` state toggles to true
   - Form inputs become enabled

2. **Click section tabs:**
   - Personal Information
   - Summary
   - Skills
   - Education
   - Experience
   - Projects
   - Certifications
   - Achievements

3. **Edit fields:**
   ```
   Personal Info:
   - Full Name: John Doe → Jane Doe
   - Email: john@example.com → jane@example.com
   ```

4. **Click "Save Changes"**

**What happens backend:**
```
PUT /api/v1/resumes/{id}
Body: {
  resume_data: {
    personal: {
      full_name: "Jane Doe",
      email: "jane@example.com",
      ...
    },
    ...
  }
}
↓
Validate input (Pydantic)
↓
Find resume by ID
↓
Check ownership (user_id matches)
↓
Update resume_data in database
↓
Return updated resume
```

**Database update:**
```sql
UPDATE resumes
SET resume_data = '{"personal": {"full_name": "Jane Doe", ...}, ...}',
    updated_at = NOW()
WHERE id = 'resume-uuid'
  AND user_id = 'user-uuid';
```

**What happens frontend:**
```
updateMutation executes
↓
Optimistic update (local state changes immediately)
↓
API call completes
↓
TanStack Query invalidates cache
↓
Re-fetches resume data
↓
UI updates with server data
↓
Shows toast "Resume updated successfully!"
```

---

## ATS Analysis

### Flow

1. **Click "Show ATS Analysis"**
   - `showATS` state toggles to true
   - ATSAnalysisCard component renders

2. **If no analysis exists, click "Run ATS Analysis"**

**What happens backend:**
```
POST /api/v1/resumes/{id}/analyze
↓
Fetch resume from database
↓
Run ATS engine:
  ├─ Contact Information Check (15 points)
  │  ├─ Has email? (+5)
  │  ├─ Has phone? (+5)
  │  └─ Has LinkedIn? (+5)
  │
  ├─ Section Structure Check (20 points)
  │  ├─ Has summary? (+5)
  │  ├─ Has experience/projects? (+5)
  │  ├─ Has education? (+5)
  │  └─ Has skills? (+5)
  │
  ├─ Formatting Check (25 points)
  │  ├─ Single column layout? (+10)
  │  ├─ No images? (+5)
  │  ├─ No tables? (+5)
  │  └─ Standard fonts? (+5)
  │
  ├─ Keywords Check (20 points)
  │  ├─ Technical skills present? (+10)
  │  └─ Action verbs used? (+10)
  │
  ├─ Readability Check (10 points)
  │  ├─ Clear sections? (+5)
  │  └─ Bullet points? (+5)
  │
  └─ File Structure Check (10 points)
     ├─ PDF format? (+5)
     └─ Reasonable length? (+5)
↓
Calculate overall score (sum / 100)
↓
Extract keywords (regex + NLP)
↓
Generate suggestions based on low scores
↓
Save analysis to database
↓
Return ATSAnalysis object
```

**Analysis result:**
```json
{
  "overall_score": 82,
  "categories": {
    "contact_information": {
      "score": 15,
      "max_score": 15,
      "details": ["Email present", "Phone present", "LinkedIn present"]
    },
    "section_structure": {
      "score": 18,
      "max_score": 20,
      "details": ["Missing achievements section"]
    },
    "formatting": {
      "score": 20,
      "max_score": 25,
      "details": ["Contains table - ATS may have issues"]
    },
    "keywords": {
      "score": 16,
      "max_score": 20,
      "details": ["Good technical keywords", "Could use more action verbs"]
    },
    "readability": {
      "score": 8,
      "max_score": 10,
      "details": ["Some sections lack clear structure"]
    },
    "file_structure": {
      "score": 5,
      "max_score": 10,
      "details": ["Resume is 4 pages - consider reducing to 1-2 pages"]
    }
  },
  "keywords_found": ["Python", "React", "AWS", "Docker", "PostgreSQL"],
  "keywords_missing": ["Kubernetes", "CI/CD", "Microservices"],
  "suggestions": [
    {
      "category": "Formatting",
      "priority": "high",
      "suggestion": "Remove tables and use bullet points instead",
      "impact": "Tables can confuse ATS parsers, reducing match rate by up to 40%"
    },
    {
      "category": "Keywords",
      "priority": "medium",
      "suggestion": "Add missing technical keywords: Kubernetes, CI/CD",
      "impact": "Including relevant keywords can increase ATS match score by 20%"
    },
    {
      "category": "File Structure",
      "priority": "low",
      "suggestion": "Reduce resume to 1-2 pages for better readability",
      "impact": "Shorter resumes are more likely to be read fully"
    }
  ]
}
```

**What happens frontend:**
```
analyzeMutation executes
↓
Shows loading spinner
↓
Receives analysis
↓
Displays:
  ├─ Large overall score (82%)
  ├─ Category breakdown with progress bars
  ├─ Keywords found (green badges)
  ├─ Keywords missing (yellow badges)
  └─ Improvement suggestions (priority-coded)
↓
Shows toast "ATS analysis complete!"
```

---

## AI Improvements

### Flow

1. **Click "AI Improvements"**
   - AIImprovementCard component renders

2. **Select section:**
   - Summary ✓
   - Experience
   - Projects
   - Achievements

3. **Select improvement types:**
   - Grammar & Spelling ✓
   - Action Verbs ✓
   - Professional Tone
   - Clarity & Conciseness

4. **Click "Generate AI Improvement"**

**What happens backend:**
```
POST /api/v1/resumes/{id}/improve
Body: {
  section_type: "summary",
  improvement_types: ["grammar", "action_verbs"]
}
↓
Fetch resume from database
↓
Extract original section content
↓
Build Claude API prompt:
  ```
  You are a professional resume writer.
  Improve the following summary section.
  Focus on: grammar and action verbs.
  Preserve all facts and achievements.
  Make it concise and impactful.
  
  Original:
  "I am software engineer with 5 year experience. 
   I work on web applications and databases."
  ```
↓
Call Claude API (temperature 0.7)
↓
Receive improved content:
  "Accomplished software engineer with 5 years of 
   experience building scalable web applications and 
   designing robust database architectures."
↓
Save improvement to database
↓
Return AIImprovement object
```

**What happens frontend:**
```
improveMutation executes
↓
Shows "AI is analyzing..." loading state
↓
Receives improvement
↓
Displays side-by-side comparison:
  ┌─────────────────────────────────────┐
  │ Original                            │
  │ "I am software engineer with 5      │
  │  year experience..."                │
  └─────────────────────────────────────┘
  ┌─────────────────────────────────────┐
  │ Improved ✨                          │
  │ "Accomplished software engineer     │
  │  with 5 years of experience..."     │
  └─────────────────────────────────────┘
↓
Shows [Reject] and [Apply] buttons
```

5. **Click "Apply"**

**What happens backend:**
```
POST /api/v1/improvements/{improvement_id}/apply
↓
Fetch improvement from database
↓
Fetch resume
↓
Replace original content with improved content
↓
Mark improvement as applied
↓
Update resume in database
↓
Return success
```

**What happens frontend:**
```
applyMutation executes
↓
Updates resume in TanStack Query cache
↓
Invalidates resume queries (triggers refetch)
↓
Shows toast "Improvement applied!"
↓
Clears improvement from display
```

---

## Export

### Flow

1. **Click "Export" button**
   - Navigate to `/resume/{id}/export`
   - ExportPage component loads

2. **Select format:**
   - PDF (ATS-Optimized) ✓ [Recommended]
   - DOCX (Word) [Coming Soon]

3. **Click "Export as PDF"**

**What happens backend:**
```
POST /api/v1/resumes/{id}/export
Body: {
  format: "pdf"
}
↓
Fetch resume from database
↓
Initialize ReportLab PDF canvas
↓
Generate ATS-optimized PDF:
  ├─ Single column layout
  ├─ Standard font (Arial 11pt)
  ├─ Clear section headings (bold, 14pt)
  ├─ Bullet points for lists
  ├─ Consistent spacing
  └─ No images, tables, columns
↓
Example structure:
  ┌───────────────────────────────────┐
  │ JOHN DOE                          │
  │ john@example.com | +1-234-567-8900│
  │ linkedin.com/in/johndoe           │
  ├───────────────────────────────────┤
  │ PROFESSIONAL SUMMARY              │
  │ Accomplished software engineer... │
  ├───────────────────────────────────┤
  │ EXPERIENCE                        │
  │ Senior Software Engineer          │
  │ Tech Corp | Jan 2020 - Dec 2023   │
  │ • Led team of 5 engineers         │
  │ • Built microservices architecture│
  ├───────────────────────────────────┤
  │ SKILLS                            │
  │ Languages: Python, JavaScript...  │
  └───────────────────────────────────┘
↓
Save PDF to temp file
↓
Upload to S3:
  Key: {user_id}/exports/{timestamp}-resume.pdf
↓
Generate presigned URL (1 hour expiry)
↓
Create export record in database
↓
Return {file_url: presigned_url}
```

**What happens frontend:**
```
exportMutation executes
↓
Shows loading state "Generating..."
↓
Receives {file_url}
↓
Shows toast "Export ready! Downloading..."
↓
Triggers download:
  const link = document.createElement('a')
  link.href = file_url
  link.download = 'resume.pdf'
  link.click()
↓
Browser downloads PDF
↓
Invalidates export history query
```

**Export history:**
```
GET /api/v1/resumes/{id}/exports
↓
Returns list of previous exports:
[
  {
    id: "export-uuid-1",
    format: "pdf",
    created_at: "2024-08-06T01:30:00Z",
    file_url: "https://..."
  },
  ...
]
```

---

## Settings

### What You See

**Profile Information:**
- Full Name: John Doe (disabled input)
- Email: john@example.com (disabled input)
- Account Status: Active (badge)

**Change Password:**
- Current Password
- New Password
- Confirm New Password
- [Update Password] button

**Appearance:**
- Theme toggle button (Light Mode / Dark Mode)

**Danger Zone:**
- Delete Account button (disabled for safety)

### Change Password Flow

1. **Fill form:**
   ```
   Current Password: password123
   New Password: newpassword456
   Confirm New Password: newpassword456
   ```

2. **Click "Update Password"**

**What happens backend:**
```
POST /api/v1/auth/change-password
Body: {
  current_password: "password123",
  new_password: "newpassword456"
}
↓
Fetch user from database
↓
Verify current password (bcrypt.verify)
↓
Validate new password (min 8 chars)
↓
Hash new password (bcrypt, cost 12)
↓
Update user in database
↓
Invalidate all refresh tokens (force re-login on other devices)
↓
Return success
```

**What happens frontend:**
```
changePasswordMutation executes
↓
Shows loading state on button
↓
On success:
  ├─ Shows toast "Password changed successfully"
  ├─ Clears form
  └─ Optionally: force logout and redirect to login
```

---

## Theme Toggle

### Flow

**Click sun/moon icon in navbar**

**What happens:**
```
toggleTheme() function called
↓
Zustand store updates: theme = 'dark' (or 'light')
↓
Persisted to localStorage: 'urcv_theme'
↓
applyTheme() called:
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
↓
Tailwind CSS dark: variants activate
↓
All colors change via CSS variables
```

**CSS variables (example):**
```css
:root {
  --background: 0 0% 100%;  /* white */
  --foreground: 222.2 84% 4.9%;  /* dark text */
}

.dark {
  --background: 222.2 84% 4.9%;  /* dark blue */
  --foreground: 210 40% 98%;  /* light text */
}
```

**Components automatically update:**
- All `bg-background` classes → use CSS variable
- All `text-foreground` classes → use CSS variable
- Smooth transition (~200ms)

---

## Logout

### Flow

**Click "Logout" button in navbar**

**What happens backend:**
```
POST /api/v1/auth/logout
↓
Extract refresh token from request
↓
Delete refresh token from database
↓
Return success
```

**What happens frontend:**
```
logoutMutation executes
↓
Clears localStorage:
  - Remove 'urcv_tokens'
↓
Clears Zustand store:
  - user = null
  - isAuthenticated = false
↓
Clears TanStack Query cache:
  - queryClient.clear()
↓
Shows toast "Logged out successfully"
↓
Navigates to /login
```

**Protected routes:**
- ProtectedRoute component checks `isAuthenticated`
- If false, redirects to /login
- User cannot access dashboard, upload, etc.

---

## Complete Data Flow Example

### Scenario: Upload Resume → Edit → Analyze → Export

```
1. USER UPLOADS RESUME
   ↓
   POST /api/v1/resumes/upload (file)
   ↓
   Backend parses PDF → Resume JSON
   ↓
   Saves to PostgreSQL (JSONB column)
   ↓
   Uploads PDF to S3/MinIO
   ↓
   Returns resume object
   ↓
   Frontend navigates to /resume/{id}

2. USER VIEWS RESUME
   ↓
   GET /api/v1/resumes/{id}
   ↓
   Backend fetches from database
   ↓
   Returns resume with resume_data
   ↓
   Frontend displays in editor

3. USER EDITS NAME
   ↓
   Changes "John" to "Jane"
   ↓
   Clicks Save
   ↓
   PUT /api/v1/resumes/{id}
   ↓
   Backend updates resume_data (JSONB)
   ↓
   Returns updated resume
   ↓
   Frontend shows toast "Saved!"

4. USER RUNS ATS ANALYSIS
   ↓
   POST /api/v1/resumes/{id}/analyze
   ↓
   Backend runs 6-category analysis
   ↓
   Calculates scores, finds keywords
   ↓
   Saves analysis to database
   ↓
   Returns analysis object
   ↓
   Frontend displays scores & suggestions

5. USER EXPORTS PDF
   ↓
   POST /api/v1/resumes/{id}/export
   ↓
   Backend generates ATS-optimized PDF
   ↓
   Uploads to S3
   ↓
   Creates presigned URL
   ↓
   Returns URL
   ↓
   Frontend triggers download
   ↓
   Browser downloads PDF

TOTAL TIME: ~10 seconds
DATABASE QUERIES: 7
S3 OPERATIONS: 2
AI CALLS: 0 (in this flow)
```

---

## Architecture Summary

### Request Flow
```
User Action
  ↓
Frontend Component
  ↓
Custom Hook (useResumes, useAuth, etc.)
  ↓
TanStack Query (caching, loading states)
  ↓
Service Layer (resume.service.ts)
  ↓
API Client (axios with interceptors)
  ↓
HTTP Request → Backend FastAPI
  ↓
Router (auth.py, resume.py, etc.)
  ↓
Service Layer (auth/service.py, etc.)
  ↓
Repository/ORM (SQLAlchemy)
  ↓
PostgreSQL Database
```

### State Management
```
Server State (TanStack Query):
- Resume data
- User data
- ATS analysis
- Export history
- Cached for 5 minutes
- Background refetching

Client State (Zustand):
- Theme (persisted)
- Auth status (persisted)
- Current resume context
- UI state
```

### Authentication Flow
```
Login
  ↓
JWT Access Token (15 min)
JWT Refresh Token (7 days)
  ↓
Stored in localStorage
  ↓
Axios interceptor adds to headers
  ↓
Backend validates JWT
  ↓
On 401: Auto-refresh via refresh token
  ↓
Retry original request
```

---

## Success Checklist

After following this walkthrough, you should be able to:

- [x] Start the application (backend + frontend)
- [x] Register a new user account
- [x] Login with credentials
- [x] See dashboard with statistics
- [x] Upload a PDF resume
- [x] View parsed resume data
- [x] Edit resume sections
- [x] Save changes
- [x] Run ATS analysis
- [x] See scores and suggestions
- [x] Generate AI improvements (with API key)
- [x] Apply improvements
- [x] Export to PDF
- [x] Download exported file
- [x] Change password
- [x] Toggle dark/light theme
- [x] Logout

**Congratulations! You've completed the full URCV walkthrough! 🎉**

---

**For more details, see:**
- [QUICKSTART.md](QUICKSTART.md) - Setup guide
- [BACKEND_COMPLETE.md](BACKEND_COMPLETE.md) - Backend docs
- [FRONTEND_COMPLETE.md](FRONTEND_COMPLETE.md) - Frontend docs
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Overall status

