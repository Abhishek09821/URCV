"""
Verify backend setup and configuration.
Run this to check if everything is configured correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.infrastructure.database import check_db_connection


async def verify_database():
    """Verify database connection."""
    print("🔍 Checking database connection...")
    try:
        is_connected = await check_db_connection()
        if is_connected:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def verify_configuration():
    """Verify configuration settings."""
    print("\n🔍 Checking configuration...")
    
    errors = []
    warnings = []
    
    # Check required settings
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-here-change-in-production-min-32-chars":
        errors.append("SECRET_KEY not set or using default value")
    
    if not settings.DATABASE_URL:
        errors.append("DATABASE_URL not configured")
    
    if not settings.S3_ACCESS_KEY_ID:
        warnings.append("S3_ACCESS_KEY_ID not set - file uploads will fail")
    
    if not settings.ANTHROPIC_API_KEY:
        warnings.append("ANTHROPIC_API_KEY not set - AI features will be disabled")
    
    # Print results
    if errors:
        print("❌ Configuration errors:")
        for err in errors:
            print(f"   - {err}")
    
    if warnings:
        print("⚠️  Configuration warnings:")
        for warn in warnings:
            print(f"   - {warn}")
    
    if not errors and not warnings:
        print("✅ Configuration looks good")
    
    return len(errors) == 0


def verify_imports():
    """Verify all imports work."""
    print("\n🔍 Checking imports...")
    
    try:
        from app.main import app
        from app.features.auth.service import AuthService
        from app.features.resume.service import ResumeService
        from app.features.ats.service import ATSService
        from app.features.ai.service import AIService
        from app.features.export.service import ExportService
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def print_summary():
    """Print setup summary."""
    print("\n" + "="*50)
    print("URCV Backend Setup Summary")
    print("="*50)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"API Version: {settings.APP_VERSION}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1] if settings.DATABASE_URL else 'Not configured'}")
    print(f"Redis: {settings.REDIS_URL.split('@')[-1] if settings.REDIS_URL else 'Not configured'}")
    print(f"S3 Endpoint: {settings.S3_ENDPOINT_URL or 'AWS S3'}")
    print(f"AI Enabled: {'Yes' if settings.ANTHROPIC_API_KEY else 'No'}")
    print("="*50)


async def main():
    """Run all verification checks."""
    print("🚀 URCV Backend Verification")
    print("="*50)
    
    # Run checks
    config_ok = verify_configuration()
    imports_ok = verify_imports()
    db_ok = await verify_database()
    
    # Print summary
    print_summary()
    
    # Final result
    print("\n" + "="*50)
    if config_ok and imports_ok and db_ok:
        print("✅ All checks passed! Backend is ready to run.")
        print("\nStart the server with:")
        print("  uvicorn app.main:app --reload")
        print("\nOr with Docker:")
        print("  docker-compose up backend")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
