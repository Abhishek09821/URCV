"""
MVP Configuration - Phase 1 Only
Clean, maintainable configuration for production deployment.
"""
import json
from typing import Any, Literal
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings for URCV MVP.
    Loads from environment variables with sensible defaults.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ============================================================================
    # APPLICATION
    # ============================================================================
    APP_NAME: str = "URCV"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Universal Resume Conversion & Verification"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    
    # ============================================================================
    # API
    # ============================================================================
    API_V1_PREFIX: str = "/api/v1"
    
    # ============================================================================
    # CORS - Accepts both comma-separated string and JSON array
    # ============================================================================
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    
    @property
    def cors_origins(self) -> list[str]:
        """
        Parse CORS origins from the stored string.
        
        Accepts two formats:
        1. Comma-separated: "http://localhost:3000,http://localhost:5173"
        2. JSON array: ["http://localhost:3000","http://localhost:5173"]
        
        Returns a list of origin strings.
        Never throws errors - returns empty list if parsing fails.
        """
        if not self.BACKEND_CORS_ORIGINS:
            return []
        
        origins_str = self.BACKEND_CORS_ORIGINS.strip()
        
        # Try parsing as JSON array first
        if origins_str.startswith("["):
            try:
                parsed = json.loads(origins_str)
                if isinstance(parsed, list):
                    return [str(origin).strip() for origin in parsed if origin]
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as comma-separated
                pass
        
        # Parse as comma-separated string
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    # ============================================================================
    # SECURITY
    # ============================================================================
    SECRET_KEY: str = Field(min_length=32, description="JWT signing key (min 32 characters)")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    
    # ============================================================================
    # DATABASE (PostgreSQL)
    # ============================================================================
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """Build async PostgreSQL connection string."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def database_url_sync(self) -> str:
        """Build sync PostgreSQL connection string for Alembic."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # ============================================================================
    # REDIS (Caching)
    # ============================================================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    @property
    def REDIS_URL(self) -> str:
        """Build Redis connection string."""
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ============================================================================
    # S3 STORAGE (File uploads)
    # ============================================================================
    S3_ENDPOINT_URL: str | None = None  # For MinIO (local dev)
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "urcv-files"
    S3_USE_SSL: bool = True
    
    # ============================================================================
    # FILE UPLOAD
    # ============================================================================
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]
    UPLOAD_FOLDER: str = "uploads"
    
    # ============================================================================
    # PDF PROCESSING
    # ============================================================================
    PDF_DPI: int = 300
    PDF_MAX_PAGES: int = 5
    OCR_LANGUAGE: str = "eng"
    
    # ============================================================================
    # AI SERVICES (Optional - for improvements)
    # ============================================================================
    ANTHROPIC_API_KEY: str | None = None
    AI_MODEL_CLAUDE: str = "claude-3-5-sonnet-20241022"
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7
    
    # ============================================================================
    # RATE LIMITING
    # ============================================================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # ============================================================================
    # MONITORING (Optional)
    # ============================================================================
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # ============================================================================
    # LOGGING
    # ============================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"
    
    # ============================================================================
    # RESUME PARSER
    # ============================================================================
    PARSER_VERSION: str = "1.0.0"
    PARSER_TIMEOUT_SECONDS: int = 60
    CONFIDENCE_THRESHOLD_VERIFICATION: int = 85
    CONFIDENCE_THRESHOLD_LOW: int = 60
    
    # ============================================================================
    # TEMPLATE ENGINE
    # ============================================================================
    TEMPLATE_RENDER_TIMEOUT_SECONDS: int = 30
    TEMPLATE_MAX_WORD_COUNT: int = 250
    
    # ============================================================================
    # CACHING
    # ============================================================================
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    ATS_CACHE_TTL_SECONDS: int = 86400  # 24 hours
    
    # ============================================================================
    # HELPER PROPERTIES
    # ============================================================================
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    @property
    def ai_enabled(self) -> bool:
        """Check if AI features are enabled."""
        return self.ANTHROPIC_API_KEY is not None


# Global settings instance
settings = Settings()
