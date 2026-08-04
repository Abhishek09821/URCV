"""
Resume API routes.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.features.resume.schemas import (
    ResumeDetailResponse,
    ResumeListItem,
    ResumeUpdateRequest,
    ResumeUploadResponse,
    VerifyResumeRequest,
)
from app.features.resume.service import ResumeService
from app.infrastructure.database import get_db

router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(..., description="PDF resume file"),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse resume PDF.
    
    - **file**: PDF file (max 10MB)
    
    Returns parsed resume with confidence scores.
    If confidence < 85%, user verification is needed.
    """
    # Read file data
    file_data = await file.read()
    
    # Upload and parse
    service = ResumeService(db)
    resume = await service.upload_and_parse(
        user_id=current_user.id,
        file_data=file_data,
        filename=file.filename or "resume.pdf"
    )
    
    # Calculate if verification needed
    confidence_scores = resume.confidence_scores or {}
    avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0
    
    return ResumeUploadResponse(
        id=resume.id,
        title=resume.title,
        status=resume.status,
        original_filename=resume.original_filename,
        confidence_scores=confidence_scores,
        needs_verification=avg_confidence < 85,
        created_at=resume.created_at
    )


@router.get("/", response_model=list[ResumeListItem])
async def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's resumes.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Max records to return (1-100)
    """
    service = ResumeService(db)
    resumes = await service.list_resumes(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return [
        ResumeListItem(
            id=r.id,
            title=r.title,
            status=r.status,
            is_verified=r.is_verified,
            ats_score=r.ats_score,
            created_at=r.created_at,
            updated_at=r.updated_at
        )
        for r in resumes
    ]


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: str,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed resume information.
    
    Returns complete Resume JSON with all sections.
    """
    from uuid import UUID
    
    service = ResumeService(db)
    resume = await service.get_resume(
        resume_id=UUID(resume_id),
        user_id=current_user.id
    )
    
    return ResumeDetailResponse(
        id=resume.id,
        title=resume.title,
        status=resume.status,
        original_filename=resume.original_filename,
        original_file_url=resume.original_file_url,
        resume_data=resume.resume_data,
        confidence_scores=resume.confidence_scores or {},
        is_verified=resume.is_verified,
        verification_mode=resume.verification_mode,
        ats_score=resume.ats_score,
        ats_analysis=resume.ats_analysis,
        created_at=resume.created_at,
        updated_at=resume.updated_at
    )


@router.put("/{resume_id}", response_model=ResumeDetailResponse)
async def update_resume(
    resume_id: str,
    request: ResumeUpdateRequest,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Update resume data (Resume JSON).
    
    Send complete Resume JSON with modifications.
    """
    from uuid import UUID
    
    service = ResumeService(db)
    resume = await service.update_resume_data(
        resume_id=UUID(resume_id),
        user_id=current_user.id,
        resume_data=request.resume_data
    )
    
    return ResumeDetailResponse(
        id=resume.id,
        title=resume.title,
        status=resume.status,
        original_filename=resume.original_filename,
        original_file_url=resume.original_file_url,
        resume_data=resume.resume_data,
        confidence_scores=resume.confidence_scores or {},
        is_verified=resume.is_verified,
        verification_mode=resume.verification_mode,
        ats_score=resume.ats_score,
        ats_analysis=resume.ats_analysis,
        created_at=resume.created_at,
        updated_at=resume.updated_at
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete resume (soft delete).
    """
    from uuid import UUID
    
    service = ResumeService(db)
    await service.delete_resume(
        resume_id=UUID(resume_id),
        user_id=current_user.id
    )


@router.post("/{resume_id}/verify", response_model=ResumeDetailResponse)
async def verify_resume(
    resume_id: str,
    request: VerifyResumeRequest,
    current_user: CurrentUser = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark resume as verified after user review.
    
    - **verification_mode**: perfect, verified, assisted, safe_layout
    """
    from uuid import UUID
    
    service = ResumeService(db)
    resume = await service.verify_resume(
        resume_id=UUID(resume_id),
        user_id=current_user.id,
        verification_mode=request.verification_mode
    )
    
    return ResumeDetailResponse(
        id=resume.id,
        title=resume.title,
        status=resume.status,
        original_filename=resume.original_filename,
        original_file_url=resume.original_file_url,
        resume_data=resume.resume_data,
        confidence_scores=resume.confidence_scores or {},
        is_verified=resume.is_verified,
        verification_mode=resume.verification_mode,
        ats_score=resume.ats_score,
        ats_analysis=resume.ats_analysis,
        created_at=resume.created_at,
        updated_at=resume.updated_at
    )
