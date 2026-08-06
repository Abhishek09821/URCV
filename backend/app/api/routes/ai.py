"""
AI Improvement API routes.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.features.ai.service import AIService
from app.infrastructure.database import get_db

router = APIRouter()


class ImproveSectionRequest(BaseModel):
    """Request to improve a section."""
    section_type: str = Field(..., description="Section type: project, experience, summary")
    section_index: int | None = Field(None, description="Index for arrays (projects, experience)")
    improvement_type: str = Field(..., description="Type: grammar, action_verbs, professional_tone, clarity")


class ImprovementResponse(BaseModel):
    """AI improvement response."""
    improvement_id: str
    original_content: str
    improved_content: str
    improvement_type: str


@router.post("/{resume_id}/improve", response_model=ImprovementResponse)
async def improve_section(
    resume_id: str,
    request: ImproveSectionRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI improvement for a resume section.
    
    **Improvement types:**
    - `grammar`: Fix grammar, spelling, punctuation
    - `action_verbs`: Replace weak verbs with strong action verbs
    - `professional_tone`: Improve professional tone
    - `clarity`: Make content clearer and more concise
    
    **Section types:**
    - `summary`: Professional summary
    - `project`: Project description (requires section_index)
    - `experience`: Work experience (requires section_index)
    
    Returns suggestion - user must explicitly apply it.
    """
    service = AIService(db)
    result = await service.improve_section(
        resume_id=UUID(resume_id),
        user_id=current_user.id,
        section_type=request.section_type,
        section_index=request.section_index,
        improvement_type=request.improvement_type
    )
    
    return ImprovementResponse(**result)


@router.post("/improvements/{improvement_id}/apply")
async def apply_improvement(
    improvement_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Apply AI improvement to resume.
    
    Updates the resume with improved content.
    """
    service = AIService(db)
    updated_data = await service.apply_improvement(
        improvement_id=UUID(improvement_id),
        user_id=current_user.id
    )
    
    return {"message": "Improvement applied", "resume_data": updated_data}
