"""
ATS service - handles ATS analysis.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundError
from app.core.logging import get_logger
from app.domain.schemas.resume_schema import ResumeJSON
from app.features.ats.engine import ATSAnalyzer
from app.infrastructure.database.models import Resume

logger = get_logger(__name__)


class ATSService:
    """ATS analysis service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.analyzer = ATSAnalyzer()
    
    async def analyze_resume(self, resume_id: UUID, user_id: UUID) -> dict:
        """
        Analyze resume for ATS compatibility.
        
        Args:
            resume_id: Resume ID
            user_id: User ID (for authorization)
            
        Returns:
            ATS analysis with score and suggestions
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
        
        # Analyze
        analysis = self.analyzer.analyze(resume_json)
        
        # Update resume with ATS data
        resume.ats_score = analysis["overall_score"]
        resume.ats_analysis = analysis
        resume.last_ats_check_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(
            "ATS analysis complete",
            extra={
                "resume_id": str(resume_id),
                "score": analysis["overall_score"]
            }
        )
        
        return analysis
