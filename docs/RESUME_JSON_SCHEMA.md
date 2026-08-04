# Resume JSON Schema

## The Source of Truth

This is the internal model that represents every resume in URCV. All features read from and write to this schema.

## Schema Version: 1.0.0

```typescript
interface ResumeJSON {
  version: string; // "1.0.0"
  
  personal: PersonalInfo;
  summary?: string;
  education: Education[];
  projects: Project[];
  experience: Experience[];
  skills: Skills;
  certifications: Certification[];
  achievements: Achievement[];
  
  // Parser metadata
  _meta: MetaData;
}

interface PersonalInfo {
  fullName: string;
  email?: string;
  phone?: string;
  location?: Location;
  links?: Link[];
  photo?: string; // URL or base64
}

interface Location {
  city?: string;
  state?: string;
  country?: string;
  full?: string; // "San Francisco, CA, USA"
}

interface Link {
  type: LinkType;
  url: string;
  display?: string; // How to display it
}

type LinkType = 
  | "linkedin" 
  | "github" 
  | "portfolio" 
  | "twitter" 
  | "personal_website"
  | "other";

interface Education {
  id: string; // UUID for tracking
  institution: string;
  degree?: string;
  field?: string;
  location?: string;
  startDate?: DateInfo;
  endDate?: DateInfo;
  gpa?: string;
  grade?: string;
  achievements?: string[];
  relevant_coursework?: string[];
  
  _confidence?: number; // 0-100
}

interface DateInfo {
  month?: number; // 1-12
  year: number;
  display?: string; // "Jan 2020"
}

interface Project {
  id: string;
  title: string;
  description: string;
  technologies?: string[];
  startDate?: DateInfo;
  endDate?: DateInfo;
  current?: boolean;
  links?: Link[];
  highlights?: string[];
  team_size?: number;
  role?: string;
  
  _confidence?: number;
  _wordCount?: number; // For overflow detection
}

interface Experience {
  id: string;
  company: string;
  position: string;
  location?: string;
  startDate?: DateInfo;
  endDate?: DateInfo;
  current?: boolean;
  description?: string;
  responsibilities?: string[];
  achievements?: string[];
  technologies?: string[];
  
  _confidence?: number;
  _wordCount?: number;
}

interface Skills {
  technical?: SkillCategory[];
  languages?: LanguageSkill[];
  other?: string[];
  
  _confidence?: number;
}

interface SkillCategory {
  category: string; // "Programming Languages", "Frameworks", etc.
  skills: string[];
}

interface LanguageSkill {
  language: string;
  proficiency?: string; // "Native", "Fluent", "Professional", "Basic"
}

interface Certification {
  id: string;
  name: string;
  issuer: string;
  issueDate?: DateInfo;
  expiryDate?: DateInfo;
  credentialId?: string;
  credentialUrl?: string;
  
  _confidence?: number;
}

interface Achievement {
  id: string;
  title: string;
  description?: string;
  date?: DateInfo;
  issuer?: string;
  
  _confidence?: number;
}

interface MetaData {
  // Parser info
  parsedAt: string; // ISO timestamp
  parserVersion: string;
  
  // Confidence scores per section
  confidence: {
    personal: number;
    summary: number;
    education: number;
    projects: number;
    experience: number;
    skills: number;
    certifications: number;
    achievements: number;
  };
  
  // Original PDF info
  originalFilename: string;
  originalFileUrl: string;
  pageCount: number;
  
  // Extraction methods used
  extractionMethods: {
    text: boolean; // PyMuPDF/pdfplumber text extraction
    ocr: boolean; // OCR fallback used
    ai: boolean; // AI-assisted extraction
  };
  
  // Layout detection
  detectedLayout?: {
    columns: number;
    hasPhoto: boolean;
    hasHeader: boolean;
    hasFooter: boolean;
    primaryFont?: string;
    fontSize?: number;
  };
  
  // Warnings
  warnings?: string[];
  
  // Last modified
  lastModified: string; // ISO timestamp
  modifiedBy: "parser" | "user" | "ai";
}
```

## Validation Rules

### Required Fields
- `personal.fullName` - MUST be present
- `version` - MUST match current schema version
- `_meta.parsedAt` - MUST be valid ISO timestamp

### Constraints
- All dates MUST be valid (year >= 1900, year <= current year + 10)
- Email MUST match email regex if present
- Phone MUST be valid format if present
- URLs MUST be valid if present
- Confidence scores MUST be 0-100
- IDs MUST be valid UUIDs

### Normalization
- All strings trimmed
- URLs normalized (add https:// if missing)
- Dates converted to consistent format
- Empty arrays removed
- Null/undefined values removed

## Field Mappings for Templates

Different templates require different fields. Here's how fields map:

```typescript
interface TemplateFieldMapping {
  required: string[]; // Fields that MUST be present
  optional: string[]; // Fields that MAY be present
  hidden: string[];   // Fields that won't be displayed
  customFields?: Record<string, any>; // Template-specific fields
}

// Example: Amity University Template
const amityMapping: TemplateFieldMapping = {
  required: [
    "personal.fullName",
    "personal.email",
    "personal.phone",
    "education",
    "skills.technical"
  ],
  optional: [
    "personal.photo",
    "summary",
    "projects",
    "experience",
    "certifications",
    "achievements"
  ],
  hidden: [],
  customFields: {
    rollNumber: "",
    batch: "",
    branch: ""
  }
};
```

## Version Migration

When schema changes, we maintain backward compatibility:

```typescript
interface SchemaMigration {
  from: string; // "1.0.0"
  to: string;   // "1.1.0"
  migrate: (oldData: any) => ResumeJSON;
}

// Example migration
const migration_1_0_to_1_1: SchemaMigration = {
  from: "1.0.0",
  to: "1.1.0",
  migrate: (data) => {
    // Add new fields with defaults
    // Transform changed fields
    // Remove deprecated fields
    return migratedData;
  }
};
```

## Storage Strategy

1. **Database**: Full Resume JSON stored in JSONB column
2. **Validation**: Pydantic models in backend enforce schema
3. **TypeScript**: Zod schemas in frontend enforce schema
4. **Indexing**: Key fields indexed for search (GIN indexes)

## Example Resume JSON

```json
{
  "version": "1.0.0",
  "personal": {
    "fullName": "Rahul Sharma",
    "email": "rahul.sharma@email.com",
    "phone": "+91-9876543210",
    "location": {
      "city": "Noida",
      "state": "Uttar Pradesh",
      "country": "India"
    },
    "links": [
      {
        "type": "linkedin",
        "url": "https://linkedin.com/in/rahulsharma",
        "display": "rahulsharma"
      },
      {
        "type": "github",
        "url": "https://github.com/rahulsharma",
        "display": "rahulsharma"
      }
    ]
  },
  "summary": "Final year Computer Science student with expertise in full-stack development and machine learning. Seeking SDE opportunities.",
  "education": [
    {
      "id": "ed-1",
      "institution": "Amity University",
      "degree": "Bachelor of Technology",
      "field": "Computer Science and Engineering",
      "location": "Noida, UP",
      "startDate": {
        "month": 8,
        "year": 2020,
        "display": "Aug 2020"
      },
      "endDate": {
        "month": 6,
        "year": 2024,
        "display": "June 2024"
      },
      "gpa": "8.9/10",
      "achievements": [
        "Dean's List for 6 consecutive semesters"
      ],
      "_confidence": 98
    }
  ],
  "projects": [
    {
      "id": "proj-1",
      "title": "E-Commerce Platform with Microservices",
      "description": "Built a scalable e-commerce platform using microservices architecture with React, Node.js, and MongoDB",
      "technologies": ["React", "Node.js", "MongoDB", "Docker", "Kubernetes"],
      "startDate": {
        "month": 1,
        "year": 2024
      },
      "endDate": {
        "month": 4,
        "year": 2024
      },
      "highlights": [
        "Handled 10,000+ concurrent users with 99.9% uptime",
        "Implemented JWT authentication and role-based access control",
        "Reduced API response time by 40% through caching"
      ],
      "links": [
        {
          "type": "github",
          "url": "https://github.com/rahulsharma/ecommerce"
        }
      ],
      "_confidence": 95,
      "_wordCount": 87
    }
  ],
  "experience": [
    {
      "id": "exp-1",
      "company": "TechCorp India",
      "position": "Software Development Intern",
      "location": "Bangalore, India",
      "startDate": {
        "month": 6,
        "year": 2023
      },
      "endDate": {
        "month": 8,
        "year": 2023
      },
      "responsibilities": [
        "Developed RESTful APIs using FastAPI and PostgreSQL",
        "Collaborated with cross-functional teams on feature development",
        "Wrote unit tests achieving 85% code coverage"
      ],
      "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"],
      "_confidence": 92,
      "_wordCount": 64
    }
  ],
  "skills": {
    "technical": [
      {
        "category": "Programming Languages",
        "skills": ["Python", "JavaScript", "TypeScript", "Java", "C++"]
      },
      {
        "category": "Web Technologies",
        "skills": ["React", "Node.js", "FastAPI", "Django", "Express"]
      },
      {
        "category": "Databases",
        "skills": ["PostgreSQL", "MongoDB", "Redis"]
      },
      {
        "category": "DevOps",
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD"]
      }
    ],
    "languages": [
      {
        "language": "English",
        "proficiency": "Fluent"
      },
      {
        "language": "Hindi",
        "proficiency": "Native"
      }
    ],
    "_confidence": 100
  },
  "certifications": [
    {
      "id": "cert-1",
      "name": "AWS Certified Developer Associate",
      "issuer": "Amazon Web Services",
      "issueDate": {
        "month": 3,
        "year": 2024
      },
      "credentialId": "AWS-CDA-123456",
      "_confidence": 100
    }
  ],
  "achievements": [
    {
      "id": "ach-1",
      "title": "Winner - Smart India Hackathon 2023",
      "description": "Led team of 6 to develop AI-powered healthcare solution",
      "date": {
        "month": 8,
        "year": 2023
      },
      "_confidence": 95
    }
  ],
  "_meta": {
    "parsedAt": "2024-01-15T10:30:00Z",
    "parserVersion": "1.0.0",
    "confidence": {
      "personal": 100,
      "summary": 95,
      "education": 98,
      "projects": 95,
      "experience": 92,
      "skills": 100,
      "certifications": 100,
      "achievements": 95
    },
    "originalFilename": "Rahul_Sharma_Resume.pdf",
    "originalFileUrl": "s3://urcv-uploads/user123/original/abc123.pdf",
    "pageCount": 1,
    "extractionMethods": {
      "text": true,
      "ocr": false,
      "ai": true
    },
    "detectedLayout": {
      "columns": 1,
      "hasPhoto": false,
      "hasHeader": true,
      "hasFooter": false,
      "primaryFont": "Arial",
      "fontSize": 11
    },
    "warnings": [],
    "lastModified": "2024-01-15T10:30:00Z",
    "modifiedBy": "parser"
  }
}
```

## Benefits of This Schema

1. **Single Source of Truth**: All features work with same data structure
2. **Type Safety**: Full TypeScript/Pydantic validation
3. **Flexible**: Supports all resume formats
4. **Trackable**: IDs and confidence scores for everything
5. **Extensible**: Easy to add new fields without breaking old data
6. **Searchable**: JSONB indexing enables fast queries
7. **Auditable**: Metadata tracks all changes
8. **Mobile-Ready**: Simple structure easy to edit on phones
