"""
SQLAlchemy ORM models for the database.
Maps to PostgreSQL schema with proper relationships and indexes.
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, UUID
from sqlalchemy.orm import relationship

from app.infrastructure.database.base import Base


class User(Base):
    """User account model."""
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified_at = Column(DateTime)
    last_login_at = Column(DateTime)
    
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    ai_improvements = relationship("AIImprovement", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_created_at", "created_at", postgresql_using="btree"),
    )


class Resume(Base):
    """Resume model - stores parsed resume data."""
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False, default="Untitled Resume")
    original_filename = Column(String(500))
    original_file_url = Column(Text, nullable=False)
    
    status = Column(
        String(50),
        nullable=False,
        default="uploaded",
        index=True
    )
    
    # Resume JSON (source of truth)
    resume_data = Column(JSONB, nullable=False, default=dict)
    
    # Parser metadata
    parser_version = Column(String(50))
    parsed_at = Column(DateTime)
    confidence_scores = Column(JSONB, default=dict)
    
    # Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime)
    verification_mode = Column(String(50))
    
    # ATS
    ats_score = Column(Integer)
    ats_analysis = Column(JSONB, default=dict)
    last_ats_check_at = Column(DateTime)
    
    # Soft delete
    deleted_at = Column(DateTime, index=True)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    exports = relationship("Export", back_populates="resume", cascade="all, delete-orphan")
    jd_matches = relationship("JDMatch", back_populates="resume", cascade="all, delete-orphan")
    ai_improvements = relationship("AIImprovement", back_populates="resume", cascade="all, delete-orphan")
    verification_sessions = relationship("VerificationSession", back_populates="resume", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('uploaded', 'parsing', 'parsed', 'verification_needed', 'verified', 'ready', 'error')",
            name="valid_status"
        ),
        CheckConstraint(
            "verification_mode IS NULL OR verification_mode IN ('perfect', 'verified', 'assisted', 'safe_layout')",
            name="valid_mode"
        ),
        Index("idx_resumes_user_id", "user_id"),
        Index("idx_resumes_status", "status"),
        Index("idx_resumes_created_at", "created_at", postgresql_using="btree"),
        Index("idx_resumes_deleted_at", "deleted_at", postgresql_where="deleted_at IS NULL"),
        Index("idx_resumes_data_gin", "resume_data", postgresql_using="gin"),
    )


class Template(Base):
    """Resume template model."""
    
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    
    description = Column(Text)
    thumbnail_url = Column(Text)
    preview_url = Column(Text)
    
    # Template definition
    template_schema = Column(JSONB, nullable=False)
    layout_config = Column(JSONB, nullable=False)
    style_config = Column(JSONB, nullable=False)
    
    # Template metadata
    institution = Column(String(255), index=True)
    
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_featured = Column(Boolean, default=False, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"))
    
    # Relationships
    exports = relationship("Export", back_populates="template")
    
    __table_args__ = (
        Index("idx_templates_slug", "slug"),
        Index("idx_templates_category", "category"),
        Index("idx_templates_institution", "institution"),
        Index("idx_templates_is_active", "is_active", postgresql_where="is_active = TRUE"),
    )


class Export(Base):
    """Export record model."""
    
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("template.id", ondelete="SET NULL"))
    
    export_type = Column(String(50), nullable=False)
    file_url = Column(Text, nullable=False)
    file_size_bytes = Column(Integer)
    
    settings = Column(JSONB, default=dict)
    
    # Relationships
    resume = relationship("Resume", back_populates="exports")
    template = relationship("Template", back_populates="exports")
    
    __table_args__ = (
        Index("idx_exports_resume_id", "resume_id"),
        Index("idx_exports_created_at", "created_at", postgresql_using="btree"),
    )


class JobDescription(Base):
    """Job description model."""
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(500), nullable=False)
    company = Column(String(255))
    description = Column(Text, nullable=False)
    
    # Parsed JD data
    required_skills = Column(ARRAY(Text), default=list)
    preferred_skills = Column(ARRAY(Text), default=list)
    keywords = Column(ARRAY(Text), default=list)
    extracted_data = Column(JSONB, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="job_descriptions")
    jd_matches = relationship("JDMatch", back_populates="job_description", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_jd_user_id", "user_id"),
        Index("idx_jd_created_at", "created_at", postgresql_using="btree"),
    )


class JDMatch(Base):
    """Job description matching result model."""
    
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume.id", ondelete="CASCADE"), nullable=False)
    jd_id = Column(UUID(as_uuid=True), ForeignKey("job_description.id", ondelete="CASCADE"), nullable=False)
    
    match_score = Column(Numeric(5, 2), nullable=False)
    analysis = Column(JSONB, nullable=False)
    
    # Relationships
    resume = relationship("Resume", back_populates="jd_matches")
    job_description = relationship("JobDescription", back_populates="jd_matches")
    
    __table_args__ = (
        Index("idx_jd_matches_resume_id", "resume_id"),
        Index("idx_jd_matches_jd_id", "jd_id"),
        Index("idx_jd_matches_unique", "resume_id", "jd_id", unique=True),
    )


class AIImprovement(Base):
    """AI improvement suggestion model."""
    
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    section_type = Column(String(100), nullable=False)
    section_index = Column(Integer)
    
    original_content = Column(Text, nullable=False)
    improved_content = Column(Text, nullable=False)
    
    improvement_type = Column(String(50), nullable=False)
    
    is_applied = Column(Boolean, default=False, nullable=False)
    applied_at = Column(DateTime)
    
    ai_model = Column(String(100))
    ai_prompt_version = Column(String(50))
    
    # Relationships
    resume = relationship("Resume", back_populates="ai_improvements")
    user = relationship("User", back_populates="ai_improvements")
    
    __table_args__ = (
        Index("idx_ai_improvements_resume_id", "resume_id"),
        Index("idx_ai_improvements_user_id", "user_id"),
    )


class VerificationSession(Base):
    """Verification session model."""
    
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resume.id", ondelete="CASCADE"), nullable=False)
    
    sections_to_verify = Column(ARRAY(Text), nullable=False)
    verified_sections = Column(JSONB, default=list)
    
    status = Column(String(50), default="pending", nullable=False)
    
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Relationships
    resume = relationship("Resume", back_populates="verification_sessions")
    
    __table_args__ = (
        Index("idx_verification_resume_id", "resume_id"),
    )


class RefreshToken(Base):
    """Refresh token model for authentication."""
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_token_hash", "token_hash"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
    )


class AuditLog(Base):
    """Audit log model for tracking user actions."""
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="SET NULL"))
    
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    
    details = Column(JSONB, default=dict)
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_created_at", "created_at", postgresql_using="btree"),
        Index("idx_audit_logs_action", "action"),
    )
