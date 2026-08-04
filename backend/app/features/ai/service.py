"""
AI improvement service.
"""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.core.logging import get_logger
from app.domain.schemas.resume_schema import ResumeJSON
from app.infrastructure.ai_client.claude import claude_client
from app.infrastructure.database.models import AIImprovement, Resume

logger = get_logger(__name__)


class AIService:
    """
    AI improvement service.
    
    Architectural Decision:
    - AI suggests improvements, user decides to apply
    - Never auto-applies AI changes
    - Stores both original and improved content
    - Tracks which improvements were applied
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def improve_section(
        self,
        resume_id: UUID,
        user_id: UUID,
        section_type: str,
        section_index: int | None,
        improvement_type: str
    ) -> dict:
        """
        Generate AI improvement suggestion for a section.
        
        Args:
            resume_id: Resume ID
            user_id: User ID
            section_type: Section type (project, experience, summary, etc.)
            section_index: Index in array (for projects/experience)
            improvement_type: Type of improvement
            
        Returns:
            Improvement suggestion with original and improved content
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
        
        # Extract content to improve
        original_content = self._extract_content(
            resume_json,
            section_type,
            section_index
        )
        
        if not original_content:
            raise ValidationError(
                "Section content not found or empty",
                field="section_type"
            )
        
        # Get context for improvement
        context = self._get_context(resume_json, section_type, section_index)
        
        # Generate improvement
        improved_content = claude_client.improve_text(
            text=original_content,
            improvement_type=improvement_type,
            context=context
        )
        
        # Store improvement suggestion
        improvement = AIImprovement(
            resume_id=resume_id,
            user_id=user_id,
            section_type=section_type,
            section_index=section_index,
            original_content=original_content,
            improved_content=improved_content,
            improvement_type=improvement_type,
            is_applied=False,
            ai_model=f"claude-{claude_client.client.default_model if claude_client.client else 'unknown'}",
            ai_prompt_version="1.0"
        )
        
        self.db.add(improvement)
        await self.db.commit()
        await self.db.refresh(improvement)
        
        logger.info(
            "AI improvement generated",
            extra={
                "resume_id": str(resume_id),
                "section_type": section_type,
                "improvement_id": str(improvement.id)
            }
        )
        
        return {
            "improvement_id": str(improvement.id),
            "original_content": original_content,
            "improved_content": improved_content,
            "improvement_type": improvement_type,
            "created_at": improvement.created_at
        }
    
    async def apply_improvement(
        self,
        improvement_id: UUID,
        user_id: UUID
    ) -> dict:
        """
        Apply AI improvement to resume.
        
        Args:
            improvement_id: Improvement ID
            user_id: User ID
            
        Returns:
            Updated resume data
        """
        # Get improvement
        result = await self.db.execute(
            select(AIImprovement)
            .where(AIImprovement.id == improvement_id)
            .where(AIImprovement.user_id == user_id)
        )
        improvement = result.scalar_one_or_none()
        
        if not improvement:
            raise ResourceNotFoundError("Improvement", str(improvement_id))
        
        # Get resume
        result = await self.db.execute(
            select(Resume).where(Resume.id == improvement.resume_id)
        )
        resume = result.scalar_one_or_none()
        
        if not resume:
            raise ResourceNotFoundError("Resume", str(improvement.resume_id))
        
        # Parse Resume JSON
        resume_json = ResumeJSON.model_validate(resume.resume_data)
        
        # Apply improvement to Resume JSON
        self._apply_content(
            resume_json,
            improvement.section_type,
            improvement.section_index,
            improvement.improved_content
        )
        
        # Update metadata
        resume_json._meta.lastModified = datetime.utcnow()
        resume_json._meta.modifiedBy = "ai"
        
        # Save updated resume
        resume.resume_data = resume_json.model_dump(mode='json')
        resume.updated_at = datetime.utcnow()
        
        # Mark improvement as applied
        improvement.is_applied = True
        improvement.applied_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.info(
            "AI improvement applied",
            extra={"improvement_id": str(improvement_id)}
        )
        
        return resume.resume_data
    
    def _extract_content(
        self,
        resume_json: ResumeJSON,
        section_type: str,
        section_index: int | None
    ) -> str | None:
        """Extract content from Resume JSON."""
        if section_type == "summary":
            return resume_json.summary
        
        elif section_type == "project":
            if section_index is not None and section_index < len(resume_json.projects):
                proj = resume_json.projects[section_index]
                content = proj.description
                if proj.highlights:
                    content += "\n" + "\n".join(proj.highlights)
                return content
        
        elif section_type == "experience":
            if section_index is not None and section_index < len(resume_json.experience):
                exp = resume_json.experience[section_index]
                parts = []
                if exp.description:
                    parts.append(exp.description)
                if exp.responsibilities:
                    parts.extend(exp.responsibilities)
                if exp.achievements:
                    parts.extend(exp.achievements)
                return "\n".join(parts)
        
        return None
    
    def _get_context(
        self,
        resume_json: ResumeJSON,
        section_type: str,
        section_index: int | None
    ) -> dict:
        """Get context for improvement."""
        context = {}
        
        if section_type == "project" and section_index is not None:
            if section_index < len(resume_json.projects):
                proj = resume_json.projects[section_index]
                context["title"] = proj.title
                context["technologies"] = proj.technologies
        
        elif section_type == "experience" and section_index is not None:
            if section_index < len(resume_json.experience):
                exp = resume_json.experience[section_index]
                context["role"] = exp.position
                context["company"] = exp.company
        
        return context
    
    def _apply_content(
        self,
        resume_json: ResumeJSON,
        section_type: str,
        section_index: int | None,
        improved_content: str
    ) -> None:
        """Apply improved content to Resume JSON."""
        if section_type == "summary":
            resume_json.summary = improved_content
        
        elif section_type == "project" and section_index is not None:
            if section_index < len(resume_json.projects):
                # Split improved content back into description and highlights
                lines = improved_content.split("\n")
                resume_json.projects[section_index].description = lines[0] if lines else improved_content
                if len(lines) > 1:
                    resume_json.projects[section_index].highlights = lines[1:]
        
        elif section_type == "experience" and section_index is not None:
            if section_index < len(resume_json.experience):
                # Split improved content into responsibilities
                lines = [l for l in improved_content.split("\n") if l.strip()]
                resume_json.experience[section_index].responsibilities = lines
