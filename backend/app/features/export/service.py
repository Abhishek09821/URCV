"""
Export service - handles resume export to various formats.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundError
from app.core.logging import get_logger
from app.domain.schemas.resume_schema import ResumeJSON
from app.infrastructure.database.models import Export, Resume
from app.infrastructure.pdf_processor.generator import pdf_generator
from app.infrastructure.storage.s3 import storage

logger = get_logger(__name__)


class ExportService:
    """
    Export service.
    
    Architectural Decision:
    - Supports PDF, ATS PDF, and future DOCX
    - Stores exports in S3 for download
    - Tracks export history
    - Generates presigned URLs for secure download
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_resume(
        self,
        resume_id: UUID,
        user_id: UUID,
        export_type: str = "pdf",
        template_id: UUID | None = None
    ) -> dict:
        """
        Export resume to specified format.
        
        Args:
            resume_id: Resume ID
            user_id: User ID
            export_type: Export type (pdf, ats_pdf, docx)
            template_id: Optional template ID for template-based export
            
        Returns:
            Export info with download URL
        """
        # Get resume
        result = await self.db.execute(
            select(Resume)
            .where(Resume.id == resume_id)
            .where(Resume.user_id == user_id)
            .where(Resume.deleted_at.is_(None))
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise ResourceNotFoundError("Resume", str(resume_id))
        
        # Parse Resume JSON
        resume_json = ResumeJSON.model_validate(resume.resume_data)
        
        # Generate export based on type
        if export_type in ["pdf", "ats_pdf"]:
            file_data = pdf_generator.generate_ats_pdf(resume_json)
            file_extension = ".pdf"
            content_type = "application/pdf"
        elif export_type == "docx":
            # DOCX generation would go here (not implemented yet)
            raise NotImplementedError("DOCX export not yet implemented")
        else:
            from app.core.exceptions import ValidationError
            raise ValidationError(f"Invalid export type: {export_type}")
        
        # Generate filename
        filename = f"{resume.title}_{export_type}_{datetime.utcnow().strftime('%Y%m%d')}{file_extension}"
        
        # Upload to S3
        s3_key = storage.upload_file(
            file_data,
            user_id=str(user_id),
            folder="exports",
            filename=filename
        )
        
        file_url = storage.get_public_url(s3_key)
        
        # Create export record
        export = Export(
            resume_id=resume_id,
            template_id=template_id,
            export_type=export_type,
            file_url=file_url,
            file_size_bytes=len(file_data),
            settings={"template_id": str(template_id) if template_id else None}
        )
        
        self.db.add(export)
        await self.db.commit()
        await self.db.refresh(export)
        
        # Generate presigned URL for download
        download_url = storage.get_presigned_url(s3_key, expires_in=3600)  # 1 hour
        
        logger.info(
            "Resume exported",
            extra={
                "resume_id": str(resume_id),
                "export_type": export_type,
                "export_id": str(export.id)
            }
        )
        
        return {
            "export_id": str(export.id),
            "export_type": export_type,
            "filename": filename,
            "download_url": download_url,
            "file_size_bytes": len(file_data),
            "created_at": export.created_at
        }
    
    async def get_export_history(
        self,
        resume_id: UUID,
        user_id: UUID
    ) -> list[dict]:
        """
        Get export history for a resume.
        
        Args:
            resume_id: Resume ID
            user_id: User ID
            
        Returns:
            List of exports
        """
        # Verify resume ownership
        result = await self.db.execute(
            select(Resume)
            .where(Resume.id == resume_id)
            .where(Resume.user_id == user_id)
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise ResourceNotFoundError("Resume", str(resume_id))
        
        # Get exports
        result = await self.db.execute(
            select(Export)
            .where(Export.resume_id == resume_id)
            .order_by(Export.created_at.desc())
            .limit(20)
        )
        
        exports = result.scalars().all()
        
        return [
            {
                "export_id": str(exp.id),
                "export_type": exp.export_type,
                "file_size_bytes": exp.file_size_bytes,
                "created_at": exp.created_at,
                "download_url": storage.get_presigned_url(
                    exp.file_url.split('/')[-3:],  # Extract key from URL
                    expires_in=3600
                ) if exp.file_url else None
            }
            for exp in exports
        ]
