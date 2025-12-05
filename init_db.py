"""
Initialize database - Creates all tables
Run this once before starting the server
"""

import asyncio
from app.database import create_db_and_tables

async def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    await create_db_and_tables()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())