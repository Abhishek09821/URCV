"""
Export API routes.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.features.export.service import ExportService
from app.infrastructure.database import get_db

router = APIRouter()


class ExportRequest(BaseModel):
    """Export request."""
    export_type: str = "ats_pdf"  # pdf, ats_pdf, docx
    template_id: str | None = None


class ExportResponse(BaseModel):
    """Export response."""
    export_id: str
    export_type: str
    filename: str
    download_url: str
    file_size_bytes: int


@router.post("/{resume_id}/export", response_model=ExportResponse)
async def export_resume(
    resume_id: str,
    request: ExportRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Export resume to PDF or other formats.
    
    **Export types:**
    - `pdf`: Standard PDF
    - `ats_pdf`: ATS-optimized PDF (recommended)
    - `docx`: Word document (coming soon)
    
    Returns download URL valid for 1 hour.
    """
    service = ExportService(db)
    result = await service.export_resume(
        resume_id=UUID(resume_id),
        user_id=current_user.id,
        export_type=request.export_type,
        template_id=UUID(request.template_id) if request.template_id else None
    )
    
    return ExportResponse(**result)


@router.get("/{resume_id}/exports")
async def get_export_history(
    resume_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Get export history for a resume.
    
    Returns last 20 exports with download URLs.
    """
    service = ExportService(db)
    exports = await service.get_export_history(
        resume_id=UUID(resume_id),
        user_id=current_user.id
    )
    
    return {"exports": exports}
