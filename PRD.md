URCV
Universal Resume Conversion & Verification

Tagline

Upload Any Resume. Edit Easily. Convert to Any Template.

Vision

Students spend hours converting resumes from PDF to Word, fixing broken formatting, recreating college templates, and improving ATS scores.

URCV eliminates this entire workflow.

The user uploads a PDF, verifies detected information in seconds, edits using a structured interface, converts into any college/company template, improves resume quality using AI, checks ATS compatibility, and exports a professional PDF.

No Microsoft Word.

No Canva.

No formatting headaches.

Problem Statement

Current Problems

PDF resumes are difficult to edit.
Word destroys formatting.
Every college requires a different resume template.
ATS optimization is confusing.
Mobile editing is almost impossible.
Resume improvements require copying content between ChatGPT and Word repeatedly.

URCV solves all of these inside one platform.

Target Users

Primary

College Students

Especially placement season.

Examples

Amity
LPU
VIT
SRM
Any university with mandatory resume templates
Product Principles

These are non-negotiable.

Rule 1

Never break the layout.

Rule 2

AI assists.

User controls.

Rule 3

No hidden changes.

Every modification is visible.

Rule 4

PDF is only input.

Resume JSON is the source of truth.

Rule 5

Mobile-first experience.

Every feature should work comfortably on phones.

Core Architecture
PDF Upload
        │
        ▼
Smart Resume Parser
        │
        ▼
Resume JSON
        │
        ▼
Verification Engine
        │
        ▼
Structured Resume Editor
        │
        ▼
Universal Template Engine
        │
        ├─────────────┐
        ▼             ▼
 ATS Engine      AI Improvement
        │             │
        └──────┬──────┘
               ▼
         Export Engine
               ▼
      PDF / DOCX / Template
Core Features
Feature 1
Universal Template Engine ⭐⭐⭐⭐⭐

Main USP.

Input

Any Resume

↓

Target Template

↓

Professional Output

Examples

Generic Resume → Amity
Generic Resume → MIT
Generic Resume → Harvard
Generic Resume → Company Template

Capabilities

Layout Preservation
Missing Field Detection
Required Field Detection
Font Preservation
Margin Preservation
Logo Handling
Photo Handling
Feature 2
PDF Resume Editor

Upload

↓

Auto Detection

↓

Structured Resume Form

Instead of editing on PDF

User edits

Name

Phone

Email

Education

Projects

Experience

Skills

Simple.

Fast.

Responsive.

Feature 3
Resume Parser

Pipeline

PyMuPDF

+

pdfplumber

+

OCR (Fallback)

+

Rule Engine

+

AI Detection

↓

Resume JSON
Resume JSON

Internal model

{
  "personal": {},
  "summary": "",
  "education": [],
  "projects": [],
  "experience": [],
  "skills": [],
  "certifications": [],
  "achievements": []
}

Every feature uses this.

Never edit the PDF directly.

Feature 4
Verification Engine

Every detected section receives confidence.

Example

Name
100%

Projects
95%

Experience
71%

Certificates
41%

If confidence < threshold

User verifies.

Verification methods

Tap Heading
Highlight Section
Paste Missing Content
Manual Entry

No full retyping.

Feature 5
ATS Engine

Real rule-based ATS.

No fake score.

Checks

Contact Information
Sections
Formatting
Keyword Presence
ATS Compatibility
Readability
File Structure

Returns

ATS Score

82%

Formatting

95%

Keywords

71%

Projects

88%

Suggestions
Feature 6
Job Description Matching

Upload

Resume

JD

↓

Comparison

↓

Results

Match %
Missing Skills
Missing Keywords
Recommended Improvements
Feature 7
AI Resume Improvement

Only improves.

Never rewrites entire resume.

Supports

Projects

Experience

Summary

Achievements

Grammar

Action Verbs

Professional Tone

Feature 8
Export Engine

Supports

PDF
DOCX
ATS PDF
Target Template Export
Accuracy Strategy

Not

AI Accuracy

Instead

System Accuracy

Pipeline

Auto Detect

↓

Confidence Score

↓

User Verification

↓

Manual Correction

↓

Resume JSON

↓

Template Rendering

↓

Export

This gives reliable outputs.

Layout Preservation Rules

Locked

Font Family
Font Size
Margins
Header
Footer
Alignment
Template Grid

Never automatically modified.

Overflow Rules

If section exceeds available space

Never silently change layout.

Instead

Warn user.

Example

Projects

Allowed

150 words

Current

218 words

Options

Shorten Content
Reduce Font
Continue Anyway
Conversion Modes

Perfect

100%

Everything detected.

Verified

99%

User verified.

Assisted

95%

Some manual input.

Safe Layout

90%

Missing content.

Layout preserved.

Reserved placeholders.

Mobile Experience

Everything designed for phones.

Large touch targets.

Card-based editing.

No Word-style editor.

No tiny toolbars.

UI Sections

Dashboard

Resume Upload

Resume Editor

Template Converter

ATS Analysis

JD Matching

Export

Settings

Tech Stack

Frontend

React
TypeScript
Vite
Tailwind CSS
React Hook Form
TanStack Query

Backend

Python
FastAPI
Pydantic
SQLAlchemy

Database

PostgreSQL

Storage

Supabase Storage or S3 compatible

PDF Processing

PyMuPDF
pdfplumber
OCR

AI

Claude API
Gemini (optional fallback)

Authentication

JWT
Refresh Tokens

Deployment

Docker
GitHub Actions
Vercel (Frontend)
Railway/Render/Fly.io (Backend)
Folder Structure
urcv/

frontend/

backend/

shared/

docs/

design-system/

templates/

parser/

renderer/

ats/

ai/

storage/

tests/
Roadmap
Phase 1
Authentication
Dashboard
PDF Upload
Resume Parser
Resume JSON
Structured Editor
Phase 2
Universal Template Engine
Export
Verification Engine
Phase 3
ATS Engine
JD Matching
AI Improvements
Phase 4
Performance
Testing
Security
SaaS Billing
Analytics
Success Metrics
Resume parsed successfully
Time to edit resume
Template conversion success rate
Export success rate
ATS improvement after edits
Mobile usability
User satisfaction
