"""
Initialize database with sample data for testing.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.database import get_engine
from app.infrastructure.database.base import Base


async def init_database():
    """Initialize database tables."""
    print("🔧 Initializing database...")
    
    engine = get_engine()
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully")
    print("\nTables created:")
    print("  - users")
    print("  - resumes")
    print("  - templates")
    print("  - exports")
    print("  - job_descriptions")
    print("  - jd_matches")
    print("  - ai_improvements")
    print("  - verification_sessions")
    print("  - refresh_tokens")
    print("  - audit_logs")
    print("\nYou can now run:")
    print("  python scripts/test_api.py")


if __name__ == "__main__":
    print("URCV Database Initialization")
    print("="*50)
    
    try:
        asyncio.run(init_database())
    except Exception as e:
        print(f"\n❌ Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
