"""
Resume parsing pipeline - orchestrates extraction, parsing, and validation.
"""
from datetime import datetime
from uuid import uuid4

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.schemas.resume_schema import (
    ConfidenceScores,
    DetectedLayout,
    ExtractionMethods,
    MetaData,
    PersonalInfo,
    ResumeJSON,
    Skills,
)
from app.features.resume.parser.rules import ExtractionRules
from app.infrastructure.pdf_processor.extractor import PDFExtractor

logger = get_logger(__name__)


class ResumeParser:
    """
    Main resume parsing pipeline.
    
    Architectural Decision:
    - Uses rule-based extraction first (fast, deterministic)
    - Falls back to AI for ambiguous content (not implemented yet)
    - Assigns confidence scores for user verification
    - Generates Resume JSON as source of truth
    """
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.rules = ExtractionRules()
    
    def parse(
        self,
        pdf_bytes: bytes,
        filename: str,
        file_url: str
    ) -> ResumeJSON:
        """
        Parse resume PDF into Resume JSON.
        
        Args:
            pdf_bytes: PDF file bytes
            filename: Original filename
            file_url: S3 URL where file is stored
            
        Returns:
            Complete Resume JSON
        """
        logger.info("Starting resume parsing", extra={"filename": filename})
        
        # Step 1: Extract text from PDF
        extraction_result = self.extractor.extract(pdf_bytes)
        text = extraction_result["text"]
        page_count = extraction_result["page_count"]
        
        # Step 2: Detect layout
        layout = self.extractor.detect_layout(pdf_bytes)
        
        # Step 3: Extract structured data using rules
        personal_info = self._extract_personal_info(text)
        education = self._extract_education(text)
        projects = self._extract_projects(text)
        experience = self._extract_experience(text)
        skills = self._extract_skills(text)
        certifications = self._extract_certifications(text)
        achievements = self._extract_achievements(text)
        summary = self._extract_summary(text)
        
        # Step 4: Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(
            personal_info, education, projects, experience,
            skills, certifications, achievements, summary
        )
        
        # Step 5: Build metadata
        metadata = MetaData(
            parsedAt=datetime.utcnow(),
            parserVersion=settings.PARSER_VERSION,
            confidence=confidence_scores,
            originalFilename=filename,
            originalFileUrl=file_url,
            pageCount=page_count,
            extractionMethods=ExtractionMethods(
                text=True,
                ocr=False,  # Would be True if OCR was used
                ai=False    # Would be True if AI extraction was used
            ),
            detectedLayout=DetectedLayout(
                columns=layout.get("columns", 1),
                hasPhoto=layout.get("has_images", False),
                hasHeader=layout.get("has_header", False),
                hasFooter=layout.get("has_footer", False)
            ),
            warnings=[],
            lastModified=datetime.utcnow(),
            modifiedBy="parser"
        )
        
        # Step 6: Build Resume JSON
        resume_json = ResumeJSON(
            version="1.0.0",
            personal=personal_info,
            summary=summary,
            education=education,
            projects=projects,
            experience=experience,
            skills=skills,
            certifications=certifications,
            achievements=achievements,
            _meta=metadata
        )
        
        logger.info(
            "Resume parsing complete",
            extra={
                "filename": filename,
                "overall_confidence": confidence_scores.average()
            }
        )
        
        return resume_json
    
    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """Extract personal information from text."""
        # Extract emails
        emails = self.rules.extract_email(text)
        email = emails[0] if emails else None
        
        # Extract phones
        phones = self.rules.extract_phone(text)
        phone = phones[0] if phones else None
        
        # Extract URLs
        urls = self.rules.extract_urls(text)
        links = [{"type": u["type"], "url": u["url"]} for u in urls]
        
        # Extract name (simplified - would use NER in production)
        name = self.rules.extract_name_from_top(text)
        if not name:
            name = "Unknown"  # Fallback
        
        return PersonalInfo(
            fullName=name,
            email=email,
            phone=phone,
            links=links
        )
    
    def _extract_education(self, text: str) -> list:
        """Extract education entries (simplified)."""
        # In production, this would use NER and section detection
        # For now, return empty list - would be filled by user verification
        return []
    
    def _extract_projects(self, text: str) -> list:
        """Extract project entries (simplified)."""
        return []
    
    def _extract_experience(self, text: str) -> list:
        """Extract experience entries (simplified)."""
        return []
    
    def _extract_skills(self, text: str) -> Skills:
        """Extract skills from text."""
        technical_skills = self.rules.extract_skills(text)
        
        if technical_skills:
            return Skills(
                technical=[{
                    "category": "Technical Skills",
                    "skills": technical_skills
                }],
                _confidence=80  # Medium confidence
            )
        
        return Skills(_confidence=50)
    
    def _extract_certifications(self, text: str) -> list:
        """Extract certifications (simplified)."""
        return []
    
    def _extract_achievements(self, text: str) -> list:
        """Extract achievements (simplified)."""
        return []
    
    def _extract_summary(self, text: str) -> str | None:
        """Extract professional summary (simplified)."""
        # Look for summary section in first 500 characters
        first_part = text[:500]
        if any(word in first_part.lower() for word in ['summary', 'objective', 'profile']):
            # Extract next 2-3 sentences
            sentences = first_part.split('.')
            if len(sentences) >= 2:
                return '. '.join(sentences[:2]) + '.'
        
        return None
    
    def _calculate_confidence_scores(
        self,
        personal_info: PersonalInfo,
        education: list,
        projects: list,
        experience: list,
        skills: Skills,
        certifications: list,
        achievements: list,
        summary: str | None
    ) -> ConfidenceScores:
        """
        Calculate confidence scores for each section.
        
        Confidence scoring logic:
        - 100: Extracted with high certainty
        - 80-99: Extracted with some uncertainty
        - 50-79: Partially extracted
        - 0-49: Not extracted or very uncertain
        """
        # Personal info confidence
        personal_confidence = 0
        if personal_info.fullName and personal_info.fullName != "Unknown":
            personal_confidence += 40
        if personal_info.email:
            personal_confidence += 30
        if personal_info.phone:
            personal_confidence += 30
        
        # Other sections
        summary_confidence = 75 if summary else 0
        education_confidence = 90 if education else 40
        projects_confidence = 85 if projects else 35
        experience_confidence = 85 if experience else 35
        skills_confidence = skills.confidence if skills.confidence else 50
        cert_confidence = 90 if certifications else 30
        achievement_confidence = 85 if achievements else 30
        
        return ConfidenceScores(
            personal=personal_confidence,
            summary=summary_confidence,
            education=education_confidence,
            projects=projects_confidence,
            experience=experience_confidence,
            skills=skills_confidence,
            certifications=cert_confidence,
            achievements=achievement_confidence
        )
