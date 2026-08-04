"""
Core configuration management using Pydantic Settings.
All environment variables are centrally managed here.
"""
from typing import Any, Literal
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "URCV"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Universal Resume Conversion & Verification"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: PostgresDsn | None = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: Any) -> str:
        """Build DATABASE_URL from components if not provided."""
        if isinstance(v, str):
            return v
        
        values = info.data
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values["POSTGRES_USER"],
                password=values["POSTGRES_PASSWORD"],
                host=values["POSTGRES_SERVER"],
                port=values["POSTGRES_PORT"],
                path=values["POSTGRES_DB"],
            )
        )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    REDIS_URL: RedisDsn | None = None
    
    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: str | None, info: Any) -> str:
        """Build REDIS_URL from components if not provided."""
        if isinstance(v, str):
            return v
        
        values = info.data
        password_part = f":{values['REDIS_PASSWORD']}@" if values.get("REDIS_PASSWORD") else ""
        return f"redis://{password_part}{values['REDIS_HOST']}:{values['REDIS_PORT']}/{values['REDIS_DB']}"
    
    # S3 Storage
    S3_ENDPOINT_URL: str | None = None  # For MinIO in development
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "urcv-files"
    S3_USE_SSL: bool = True
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list[str] = [".pdf"]
    UPLOAD_FOLDER: str = "uploads"
    
    # PDF Processing
    PDF_DPI: int = 300
    OCR_LANGUAGE: str = "eng"
    PDF_MAX_PAGES: int = 5
    
    # AI Services
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    AI_MODEL_CLAUDE: str = "claude-3-5-sonnet-20241022"
    AI_MODEL_GEMINI: str = "gemini-pro"
    AI_MAX_TOKENS: int = 1000
    AI_TEMPERATURE: float = 0.7
    
    # Celery
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None
    
    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker(cls, v: str | None, info: Any) -> str:
        """Use Redis URL for Celery broker if not provided."""
        return v or info.data.get("REDIS_URL", "redis://localhost:6379/0")
    
    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_backend(cls, v: str | None, info: Any) -> str:
        """Use Redis URL for Celery result backend if not provided."""
        return v or info.data.get("REDIS_URL", "redis://localhost:6379/0")
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str = "URCV"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Monitoring
    SENTRY_DSN: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # Feature Flags
    ENABLE_AI_IMPROVEMENTS: bool = True
    ENABLE_JD_MATCHING: bool = True
    ENABLE_TEMPLATE_CONVERSION: bool = True
    ENABLE_ATS_ANALYSIS: bool = True
    
    # Cache
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    ATS_CACHE_TTL_SECONDS: int = 86400  # 24 hours
    
    # Confidence Thresholds
    CONFIDENCE_THRESHOLD_VERIFICATION: int = 85
    CONFIDENCE_THRESHOLD_LOW: int = 60
    
    # Parser
    PARSER_VERSION: str = "1.0.0"
    PARSER_TIMEOUT_SECONDS: int = 60
    
    # Template
    TEMPLATE_RENDER_TIMEOUT_SECONDS: int = 30
    TEMPLATE_MAX_WORD_COUNT: int = 250  # Per section
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        if not self.DATABASE_URL:
            return ""
        return str(self.DATABASE_URL).replace("postgresql+asyncpg", "postgresql")


# Global settings instance
settings = Settings()
