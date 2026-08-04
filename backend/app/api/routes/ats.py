"""
ATS Analysis API routes.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.features.ats.service import ATSService
from app.infrastructure.database import get_db

router = APIRouter()


class ATSAnalysisResponse(BaseModel):
    """ATS analysis response."""
    overall_score: int
    breakdown: dict[str, int]
    suggestions: list[dict]
    passed: bool


@router.post("/{resume_id}/analyze", response_model=ATSAnalysisResponse)
async def analyze_ats(
    resume_id: str,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze resume for ATS compatibility.
    
    Returns:
    - **overall_score**: ATS compatibility score (0-100)
    - **breakdown**: Scores by category
    - **suggestions**: Actionable improvement suggestions
    - **passed**: Whether score is acceptable (70+)
    
    Score breakdown:
    - Contact Information: 15 points
    - Section Structure: 20 points
    - Formatting: 25 points
    - Keywords: 20 points
    - Readability: 10 points
    - File Structure: 10 points
    """
    service = ATSService(db)
    analysis = await service.analyze_resume(
        resume_id=UUID(resume_id),
        user_id=current_user.id
    )
    
    return ATSAnalysisResponse(**analysis)
