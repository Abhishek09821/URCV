"""
Resume API request/response schemas.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    """Response after resume upload."""
    id: UUID
    title: str
    status: str
    original_filename: str
    confidence_scores: dict
    needs_verification: bool
    created_at: datetime


class ResumeListItem(BaseModel):
    """Resume list item."""
    id: UUID
    title: str
    status: str
    is_verified: bool
    ats_score: int | None
    created_at: datetime
    updated_at: datetime


class ResumeDetailResponse(BaseModel):
    """Detailed resume response."""
    id: UUID
    title: str
    status: str
    original_filename: str
    original_file_url: str
    resume_data: dict
    confidence_scores: dict
    is_verified: bool
    verification_mode: str | None
    ats_score: int | None
    ats_analysis: dict | None
    created_at: datetime
    updated_at: datetime


class ResumeUpdateRequest(BaseModel):
    """Request to update resume data."""
    resume_data: dict = Field(..., description="Complete Resume JSON")


class VerifyResumeRequest(BaseModel):
    """Request to verify resume."""
    verification_mode: str = Field(default="verified", description="Verification mode")
