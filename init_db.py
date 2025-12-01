"""
Initialize database - Creates all tables
Run this once before starting the server

This script will:
1. Connect to PostgreSQL using the DATABASE_URL from .env
2. Create the 'user' table based on the User model
3. Print success or error messages
"""

import asyncio
import sys
from app.database import create_db_and_tables


async def init_db():
    """Create all tables in the database"""
    try:
        print("🔄 Creating database tables...")
        await create_db_and_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables:")
        print(f"   {type(e).__name__}: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure PostgreSQL is running")
        print("   2. Check DATABASE_URL in .env file")
        print("   3. Verify database exists: createdb -U postgres visioncrafter")
        return False


if __name__ == "__main__":
    success = asyncio.run(init_db())
    sys.exit(0 if success else 1)
