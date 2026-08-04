"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verified_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('idx_users_email', 'user', ['email'])
    op.create_index('idx_users_created_at', 'user', ['created_at'])

    # Create resumes table
    op.create_table(
        'resume',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Untitled Resume'),
        sa.Column('original_filename', sa.String(length=500), nullable=True),
        sa.Column('original_file_url', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='uploaded'),
        sa.Column('resume_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('parser_version', sa.String(length=50), nullable=True),
        sa.Column('parsed_at', sa.DateTime(), nullable=True),
        sa.Column('confidence_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('verification_mode', sa.String(length=50), nullable=True),
        sa.Column('ats_score', sa.Integer(), nullable=True),
        sa.Column('ats_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('last_ats_check_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("status IN ('uploaded', 'parsing', 'parsed', 'verification_needed', 'verified', 'ready', 'error')", name='valid_status'),
        sa.CheckConstraint("verification_mode IS NULL OR verification_mode IN ('perfect', 'verified', 'assisted', 'safe_layout')", name='valid_mode')
    )
    op.create_index('idx_resumes_user_id', 'resume', ['user_id'])
    op.create_index('idx_resumes_status', 'resume', ['status'])
    op.create_index('idx_resumes_created_at', 'resume', ['created_at'])
    op.create_index('idx_resumes_deleted_at', 'resume', ['deleted_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_resumes_data_gin', 'resume', ['resume_data'], postgresql_using='gin')

    # Create templates table
    op.create_table(
        'template',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('preview_url', sa.Text(), nullable=True),
        sa.Column('template_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('layout_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('style_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('institution', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('idx_templates_slug', 'template', ['slug'])
    op.create_index('idx_templates_category', 'template', ['category'])
    op.create_index('idx_templates_institution', 'template', ['institution'])
    op.create_index('idx_templates_is_active', 'template', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create exports table
    op.create_table(
        'export',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('export_type', sa.String(length=50), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resume.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['template.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_exports_resume_id', 'export', ['resume_id'])
    op.create_index('idx_exports_created_at', 'export', ['created_at'])

    # Create job_description table
    op.create_table(
        'job_description',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('required_skills', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('preferred_skills', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('keywords', postgresql.ARRAY(sa.Text()), nullable=True, server_default='{}'),
        sa.Column('extracted_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jd_user_id', 'job_description', ['user_id'])
    op.create_index('idx_jd_created_at', 'job_description', ['created_at'])

    # Create jd_match table
    op.create_table(
        'jd_match',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('jd_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('match_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resume.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['jd_id'], ['job_description.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jd_matches_resume_id', 'jd_match', ['resume_id'])
    op.create_index('idx_jd_matches_jd_id', 'jd_match', ['jd_id'])
    op.create_index('idx_jd_matches_unique', 'jd_match', ['resume_id', 'jd_id'], unique=True)

    # Create ai_improvement table
    op.create_table(
        'ai_improvement',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('section_type', sa.String(length=100), nullable=False),
        sa.Column('section_index', sa.Integer(), nullable=True),
        sa.Column('original_content', sa.Text(), nullable=False),
        sa.Column('improved_content', sa.Text(), nullable=False),
        sa.Column('improvement_type', sa.String(length=50), nullable=False),
        sa.Column('is_applied', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('ai_prompt_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resume.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_improvements_resume_id', 'ai_improvement', ['resume_id'])
    op.create_index('idx_ai_improvements_user_id', 'ai_improvement', ['user_id'])

    # Create verification_session table
    op.create_table(
        'verification_session',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resume_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sections_to_verify', postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column('verified_sections', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['resume_id'], ['resume.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_verification_resume_id', 'verification_session', ['resume_id'])

    # Create refresh_token table
    op.create_table(
        'refresh_token',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    op.create_index('idx_refresh_tokens_user_id', 'refresh_token', ['user_id'])
    op.create_index('idx_refresh_tokens_token_hash', 'refresh_token', ['token_hash'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_token', ['expires_at'])

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_logs_user_id', 'audit_log', ['user_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_log', ['created_at'])
    op.create_index('idx_audit_logs_action', 'audit_log', ['action'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('audit_log')
    op.drop_table('refresh_token')
    op.drop_table('verification_session')
    op.drop_table('ai_improvement')
    op.drop_table('jd_match')
    op.drop_table('job_description')
    op.drop_table('export')
    op.drop_table('template')
    op.drop_table('resume')
    op.drop_table('user')
