"""
Resume JSON Schema - The Source of Truth
All resume data follows this schema. Pydantic provides runtime validation.
"""
from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator


# Enums

class LinkType(str, Enum):
    """Types of links in personal info."""
    LINKEDIN = "linkedin"
    GITHUB = "github"
    PORTFOLIO = "portfolio"
    TWITTER = "twitter"
    PERSONAL_WEBSITE = "personal_website"
    OTHER = "other"


class LanguageProficiency(str, Enum):
    """Language proficiency levels."""
    NATIVE = "native"
    FLUENT = "fluent"
    PROFESSIONAL = "professional"
    BASIC = "basic"


class ModifiedBy(str, Enum):
    """Who last modified the resume."""
    PARSER = "parser"
    USER = "user"
    AI = "ai"


# Schemas

class DateInfo(BaseModel):
    """Date information with flexible formatting."""
    month: int | None = Field(None, ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=1900, description="Year")
    display: str | None = Field(None, description="Display format (e.g., 'Jan 2020')")
    
    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Ensure year is not in far future."""
        current_year = datetime.now().year
        if v > current_year + 10:
            raise ValueError(f"Year cannot be more than 10 years in future: {v}")
        return v
    
    def to_display(self) -> str:
        """Convert to display string."""
        if self.display:
            return self.display
        
        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        
        if self.month:
            return f"{months[self.month - 1]} {self.year}"
        return str(self.year)


class Link(BaseModel):
    """Link in personal information."""
    type: LinkType = Field(..., description="Type of link")
    url: HttpUrl | str = Field(..., description="URL")
    display: str | None = Field(None, description="Display text")
    
    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str | HttpUrl) -> str:
        """Ensure URL has protocol."""
        url_str = str(v)
        if not url_str.startswith(("http://", "https://")):
            url_str = f"https://{url_str}"
        return url_str


class Location(BaseModel):
    """Geographic location information."""
    city: str | None = None
    state: str | None = None
    country: str | None = None
    full: str | None = Field(None, description="Full location string")


class PersonalInfo(BaseModel):
    """Personal information section."""
    fullName: str = Field(..., min_length=1, description="Full name")
    email: EmailStr | None = None
    phone: str | None = None
    location: Location | None = None
    links: list[Link] = Field(default_factory=list)
    photo: str | None = Field(None, description="Photo URL or base64")


class Education(BaseModel):
    """Education entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    institution: str = Field(..., min_length=1)
    degree: str | None = None
    field: str | None = None
    location: str | None = None
    startDate: DateInfo | None = None
    endDate: DateInfo | None = None
    gpa: str | None = None
    grade: str | None = None
    achievements: list[str] = Field(default_factory=list)
    relevant_coursework: list[str] = Field(default_factory=list)
    
    # Parser metadata
    confidence: int | None = Field(None, ge=0, le=100)


class Project(BaseModel):
    """Project entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    technologies: list[str] = Field(default_factory=list)
    startDate: DateInfo | None = None
    endDate: DateInfo | None = None
    current: bool = False
    links: list[Link] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    team_size: int | None = Field(None, ge=1)
    role: str | None = None
    
    # Parser metadata
    confidence: int | None = Field(None, ge=0, le=100)
    wordCount: int | None = Field(None, ge=0)


class Experience(BaseModel):
    """Work experience entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    company: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    location: str | None = None
    startDate: DateInfo | None = None
    endDate: DateInfo | None = None
    current: bool = False
    description: str | None = None
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    
    # Parser metadata
    confidence: int | None = Field(None, ge=0, le=100)
    wordCount: int | None = Field(None, ge=0)


class SkillCategory(BaseModel):
    """Categorized skills."""
    category: str = Field(..., min_length=1)
    skills: list[str] = Field(..., min_length=1)


class LanguageSkill(BaseModel):
    """Language proficiency."""
    language: str = Field(..., min_length=1)
    proficiency: LanguageProficiency | None = None


class Skills(BaseModel):
    """Skills section."""
    technical: list[SkillCategory] = Field(default_factory=list)
    languages: list[LanguageSkill] = Field(default_factory=list)
    other: list[str] = Field(default_factory=list)
    
    # Parser metadata
    confidence: int | None = Field(None, ge=0, le=100)


class Certification(BaseModel):
    """Certification entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1)
    issuer: str = Field(..., min_length=1)
    issueDate: DateInfo | None = None
    expiryDate: DateInfo | None = None
    credentialId: str | None = None
    credentialUrl: HttpUrl | str | None = None
    
    # Parser metadata
    confidence: int | None = Field(None, ge=0, le=100)


class Achievement(BaseModel):
    """Achievement entry."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1)
    description: str | None = None
    date: DateInfo | None = None
    issuer: str | None = None
    
    # Parser metadata
    confidence: int | None = Field(None, ge=0, le=100)


class ExtractionMethods(BaseModel):
    """Methods used for extraction."""
    text: bool = Field(default=False, description="Text extraction used")
    ocr: bool = Field(default=False, description="OCR used")
    ai: bool = Field(default=False, description="AI extraction used")


class DetectedLayout(BaseModel):
    """Detected PDF layout information."""
    columns: int = Field(1, ge=1, le=3)
    hasPhoto: bool = False
    hasHeader: bool = False
    hasFooter: bool = False
    primaryFont: str | None = None
    fontSize: int | None = Field(None, ge=6, le=24)


class ConfidenceScores(BaseModel):
    """Confidence scores for each section."""
    personal: int = Field(0, ge=0, le=100)
    summary: int = Field(0, ge=0, le=100)
    education: int = Field(0, ge=0, le=100)
    projects: int = Field(0, ge=0, le=100)
    experience: int = Field(0, ge=0, le=100)
    skills: int = Field(0, ge=0, le=100)
    certifications: int = Field(0, ge=0, le=100)
    achievements: int = Field(0, ge=0, le=100)
    
    def average(self) -> float:
        """Calculate average confidence score."""
        scores = [
            self.personal,
            self.summary,
            self.education,
            self.projects,
            self.experience,
            self.skills,
            self.certifications,
            self.achievements,
        ]
        return sum(scores) / len(scores)


class MetaData(BaseModel):
    """Parser and processing metadata."""
    parsedAt: datetime = Field(default_factory=datetime.utcnow)
    parserVersion: str = Field(..., description="Parser version used")
    confidence: ConfidenceScores = Field(default_factory=ConfidenceScores)
    originalFilename: str
    originalFileUrl: str
    pageCount: int = Field(1, ge=1)
    extractionMethods: ExtractionMethods = Field(default_factory=ExtractionMethods)
    detectedLayout: DetectedLayout | None = None
    warnings: list[str] = Field(default_factory=list)
    lastModified: datetime = Field(default_factory=datetime.utcnow)
    modifiedBy: ModifiedBy = ModifiedBy.PARSER


class ResumeJSON(BaseModel):
    """
    Complete Resume JSON Schema - The Source of Truth.
    
    This is the internal model that represents every resume in URCV.
    All features read from and write to this schema.
    """
    version: str = Field(default="1.0.0", description="Schema version")
    
    # Main sections
    personal: PersonalInfo
    summary: str | None = None
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    skills: Skills = Field(default_factory=Skills)
    certifications: list[Certification] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    
    # Metadata
    meta: MetaData
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
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
                            "url": "https://linkedin.com/in/rahulsharma"
                        }
                    ]
                },
                "summary": "Final year CS student with full-stack development expertise",
                "education": [
                    {
                        "institution": "Amity University",
                        "degree": "Bachelor of Technology",
                        "field": "Computer Science",
                        "gpa": "8.9/10"
                    }
                ],
                "meta": {
                    "parserVersion": "1.0.0",
                    "originalFilename": "resume.pdf",
                    "originalFileUrl": "s3://bucket/file.pdf",
                    "pageCount": 1
                }
            }
        }
    
    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Ensure version is valid."""
        if not v or not v[0].isdigit():
            raise ValueError("Invalid version format")
        return v
    
    def get_overall_confidence(self) -> float:
        """Get overall confidence score."""
        return self.meta.confidence.average()
    
    def needs_verification(self, threshold: int = 85) -> bool:
        """Check if resume needs user verification."""
        return self.get_overall_confidence() < threshold
    
    def count_words_in_section(self, section: str, index: int | None = None) -> int:
        """Count words in a specific section for overflow detection."""
        text = ""
        
        if section == "summary" and self.summary:
            text = self.summary
        elif section == "projects" and index is not None and index < len(self.projects):
            project = self.projects[index]
            text = f"{project.description} {' '.join(project.highlights)}"
        elif section == "experience" and index is not None and index < len(self.experience):
            exp = self.experience[index]
            responsibilities = " ".join(exp.responsibilities)
            achievements = " ".join(exp.achievements)
            text = f"{exp.description or ''} {responsibilities} {achievements}"
        
        return len(text.split())
