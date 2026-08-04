"""
Resume service - handles resume CRUD, upload, parsing, verification.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    InvalidFileError,
    InvalidFileTypeError,
    FileTooLargeError,
    ResourceNotFoundError,
)
from app.core.logging import get_logger
from app.domain.schemas.resume_schema import ResumeJSON
from app.features.resume.parser.pipeline import ResumeParser
from app.infrastructure.database.models import Resume
from app.infrastructure.storage.s3 import storage

logger = get_logger(__name__)


class ResumeService:
    """
    Resume service.
    
    Architectural Decision:
    - Async processing with Celery would be ideal for parsing
    - For now, parsing happens synchronously (fast enough for MVP)
    - Resume JSON stored in JSONB column
    - Original PDF stored in S3
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = ResumeParser()
    
    async def upload_and_parse(
        self,
        user_id: UUID,
        file_data: bytes,
        filename: str
    ) -> Resume:
        """
        Upload PDF and parse resume.
        
        Args:
            user_id: User ID
            file_data: PDF file bytes
            filename: Original filename
            
        Returns:
            Created resume record
            
        Raises:
            InvalidFileTypeError: If file is not PDF
            FileTooLargeError: If file exceeds size limit
        """
        # Validate file type
        if not filename.lower().endswith('.pdf'):
            raise InvalidFileTypeError('application/pdf', ['.pdf'])
        
        # Validate file size
        if len(file_data) > settings.MAX_UPLOAD_SIZE:
            raise FileTooLargeError(settings.MAX_UPLOAD_SIZE)
        
        # Upload to S3
        s3_key = storage.upload_file(
            file_data,
            user_id=str(user_id),
            folder="original",
            filename=filename
        )
        
        file_url = storage.get_public_url(s3_key)
        
        # Create initial resume record
        resume = Resume(
            user_id=user_id,
            title=filename.replace('.pdf', ''),
            original_filename=filename,
            original_file_url=file_url,
            status="parsing",
            resume_data={}
        )
        
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        
        try:
            # Parse resume
            resume_json = self.parser.parse(file_data, filename, file_url)
            
            # Update resume with parsed data
            resume.resume_data = resume_json.model_dump(mode='json')
            resume.parser_version = settings.PARSER_VERSION
            resume.parsed_at = datetime.utcnow()
            resume.confidence_scores = resume_json._meta.confidence.model_dump()
            
            # Determine if verification is needed
            overall_confidence = resume_json.get_overall_confidence()
            if overall_confidence < settings.CONFIDENCE_THRESHOLD_VERIFICATION:
                resume.status = "verification_needed"
            else:
                resume.status = "ready"
                resume.is_verified = True
                resume.verified_at = datetime.utcnow()
                resume.verification_mode = "perfect"
            
            await self.db.commit()
            await self.db.refresh(resume)
            
            logger.info(
                "Resume parsed successfully",
                extra={
                    "resume_id": str(resume.id),
                    "user_id": str(user_id),
                    "confidence": overall_confidence
                }
            )
            
        except Exception as e:
            # Mark as error
            resume.status = "error"
            await self.db.commit()
            logger.error("Resume parsing failed", extra={"error": str(e), "resume_id": str(resume.id)})
            raise
        
        return resume
    
    async def get_resume(self, resume_id: UUID, user_id: UUID) -> Resume:
        """
        Get resume by ID.
        
        Args:
            resume_id: Resume ID
            user_id: User ID (for authorization)
            
        Returns:
            Resume record
            
        Raises:
            ResourceNotFoundError: If resume not found
        """
        result = await self.db.execute(
            select(Resume)
            .where(Resume.id == resume_id)
            .where(Resume.user_id == user_id)
            .where(Resume.deleted_at.is_(None))
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise ResourceNotFoundError("Resume", str(resume_id))
        
        return resume
    
    async def list_resumes(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> list[Resume]:
        """
        List user's resumes.
        
        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Max records to return
            
        Returns:
            List of resumes
        """
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .where(Resume.deleted_at.is_(None))
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(result.scalars().all())
    
    async def update_resume_data(
        self,
        resume_id: UUID,
        user_id: UUID,
        resume_data: dict
    ) -> Resume:
        """
        Update resume JSON data.
        
        Args:
            resume_id: Resume ID
            user_id: User ID
            resume_data: Updated resume JSON
            
        Returns:
            Updated resume
        """
        resume = await self.get_resume(resume_id, user_id)
        
        # Validate resume data with Pydantic
        resume_json = ResumeJSON.model_validate(resume_data)
        
        # Update metadata
        resume_json._meta.lastModified = datetime.utcnow()
        resume_json._meta.modifiedBy = "user"
        
        resume.resume_data = resume_json.model_dump(mode='json')
        resume.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(resume)
        
        logger.info("Resume updated", extra={"resume_id": str(resume_id)})
        
        return resume
    
    async def delete_resume(self, resume_id: UUID, user_id: UUID) -> None:
        """
        Soft delete resume.
        
        Args:
            resume_id: Resume ID
            user_id: User ID
        """
        resume = await self.get_resume(resume_id, user_id)
        
        resume.deleted_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info("Resume deleted", extra={"resume_id": str(resume_id)})
    
    async def verify_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        verification_mode: str = "verified"
    ) -> Resume:
        """
        Mark resume as verified.
        
        Args:
            resume_id: Resume ID
            user_id: User ID
            verification_mode: Verification mode (verified, assisted, etc.)
            
        Returns:
            Updated resume
        """
        resume = await self.get_resume(resume_id, user_id)
        
        resume.is_verified = True
        resume.verified_at = datetime.utcnow()
        resume.verification_mode = verification_mode
        resume.status = "ready"
        
        await self.db.commit()
        await self.db.refresh(resume)
        
        logger.info("Resume verified", extra={"resume_id": str(resume_id)})
        
        return resume
