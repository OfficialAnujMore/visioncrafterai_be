"""
Database migration script to recreate tables with Google OAuth schema
"""
import asyncio
from sqlmodel import SQLModel, text
from app.database import engine
from app.models import User  # Import User model to register it with SQLModel


async def recreate_tables():
    """Drop old tables and create new ones with Google OAuth schema"""
    async with engine.begin() as conn:
        # Drop old tables (including orphaned refreshtoken table)
        await conn.execute(text("DROP TABLE IF EXISTS refreshtoken CASCADE"))
        await conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        print("🗑️  Dropped all old tables")
        
        # Create new tables with Google OAuth schema
        await conn.run_sync(SQLModel.metadata.create_all)
        print("✅ Created user table with Google OAuth schema:")
        print("   - id (primary key)")
        print("   - google_id (unique)")
        print("   - email (unique)")
        print("   - name")
        print("   - picture")
        print("   - is_active")
        print("   - created_at")
        print("   - last_login")


if __name__ == "__main__":
    asyncio.run(recreate_tables())
