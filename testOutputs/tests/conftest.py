"""
VisionCrafterAI Backend - Shared Test Fixtures and Configuration

This module contains all shared fixtures used across the test suite:
- Database setup and teardown
- AsyncClient initialization with dependency injection
- Mock user and project creation
- JWT token generation helpers

Database: In-memory SQLite for test isolation
Async Framework: pytest-asyncio
"""

import pytest
import json
import jwt
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Add project root to path to find app module
# This script supports both locations:
# 1. /path/to/visioncrafterai_be/testOutputs/tests/ (development)
# 2. /path/to/outputs/testOutputs/tests/ (documentation)

conftest_dir = os.path.dirname(os.path.abspath(__file__))  # tests
testoutputs_dir = os.path.dirname(conftest_dir)            # testOutputs
parent_dir = os.path.dirname(testoutputs_dir)              # visioncrafterai_be OR outputs

# Try to find the app module
# If running from visioncrafterai_be/testOutputs, parent_dir is correct
# If running from outputs/testOutputs, we need to go to visioncrafterai_be
possible_roots = [
    parent_dir,  # visioncrafterai_be (when in /visioncrafterai_be/testOutputs)
    "/Users/anujmore/Development/VisionCrafterAI/visioncrafterai_be",  # fallback path
]

for root in possible_roots:
    if os.path.exists(os.path.join(root, "app")):
        sys.path.insert(0, root)
        break

from app.main import app
from app.database import get_session
from app.models import User
from app.models.project import Project
from app.config import settings
from app.utils.security import get_current_user_from_cookie


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture
async def async_db_session():
    """Create an in-memory AsyncSession for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


# ============================================================================
# CLIENT FIXTURES
# ============================================================================

@pytest.fixture
async def client_with_db(async_db_session):
    """Create AsyncClient with dependency override for database session."""
    async def get_test_session():
        yield async_db_session

    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(async_db_session, test_user):
    """Create AsyncClient with database and authentication overrides."""
    async def get_test_session():
        yield async_db_session

    # Create a valid access token for the test user
    access_token = create_access_token_for_user(test_user.id)

    # Override dependencies
    app.dependency_overrides[get_session] = get_test_session

    async def mock_get_current_user(request=None):
        return {"sub": str(test_user.id), "type": "access"}

    app.dependency_overrides[get_current_user_from_cookie] = mock_get_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Set the access token as a cookie so it's available to the app
        client.cookies.set("access_token", access_token)
        yield client

    app.dependency_overrides.clear()


# ============================================================================
# USER & PROJECT FIXTURES
# ============================================================================

@pytest.fixture
async def test_user(async_db_session):
    """Create a test user in the database."""
    user = User(
        google_id="123456789",
        email="testuser@example.com",
        name="Test User",
        picture="https://example.com/picture.jpg",
        is_active=True,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
async def test_project(async_db_session, test_user):
    """Create a test project in the database."""
    project = Project(
        file_id="test_file_123",
        user_id=test_user.id,
        title="Test Project",
        project_url="https://example.com/project.json",
        thumbnail_url="https://example.com/thumbnail.jpg",
        width=1920,
        height=1080,
        file_type="image",
        canvas_state=json.dumps({"layers": []}),
    )
    async_db_session.add(project)
    await async_db_session.commit()
    await async_db_session.refresh(project)
    return project


# ============================================================================
# TOKEN GENERATION HELPERS
# ============================================================================

@pytest.fixture
def mock_jwt_token():
    """Generate a mock JWT token for testing."""
    return create_access_token_for_user(1)


def create_access_token_for_user(user_id: int, hours: int = 1) -> str:
    """Create a valid JWT access token for a test user using app settings."""
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token_for_user(user_id: int, days: int = 7) -> str:
    """Create a valid JWT refresh token for a test user using app settings."""
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=days),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
