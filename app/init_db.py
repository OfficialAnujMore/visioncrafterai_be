"""
Initialize database - Creates all tables
Run this once before starting the server
"""

import asyncio
import sys
import os

# Add parent directory to path so we can import app module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import create_db_and_tables

async def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    await create_db_and_tables()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())