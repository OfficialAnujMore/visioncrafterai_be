"""
VisionCrafterAI Backend - Project Management Tests

This module tests all project management endpoints:
- Create project with validation
- Read single project and user's projects
- Update project (PUT and PATCH methods)
- Delete project

Tests cover CRUD operations, authorization checks, validation errors, and edge cases.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import get_session
from app.models import User
from app.models.project import Project
from app.utils.security import get_current_user_from_cookie


# ============================================================================
# PROJECT ENDPOINTS TESTS (Create, Read, Update, Delete)
# ============================================================================

@pytest.mark.asyncio
async def test_create_project_success(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-001
    Endpoint: POST /api/projects/create
    Description: Valid project creation with all required fields
    Precondition: User is authenticated
    Input: CreateProjectRequest with valid data
    Expected: 201 Created, ProjectResponse with id
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "New Project",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "image",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "New Project"


@pytest.mark.asyncio
async def test_create_project_missing_required_field(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-002
    Endpoint: POST /api/projects/create
    Description: Missing required field (title)
    Input: CreateProjectRequest missing title
    Expected: 422 Unprocessable Entity
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "image",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_invalid_file_type(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-003
    Endpoint: POST /api/projects/create
    Description: Invalid file_type value (not 'video' or 'image')
    Input: file_type = 'unknown'
    Expected: 422 Unprocessable Entity
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "New Project",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "unknown",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_with_canvas_state(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-004
    Endpoint: POST /api/projects/create
    Description: Project creation with optional canvas_state
    Input: CreateProjectRequest with canvas_state dict
    Expected: 201 Created, canvas_state preserved in response
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "Project with State",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "image",
        "canvas_state": {"layers": [{"id": 1, "name": "Layer 1"}]},
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    assert response.status_code == 201
    data = response.json()
    assert "canvas_state" in data["data"]


@pytest.mark.asyncio
async def test_get_project_success(authenticated_client, test_project, test_user):
    """
    Test Case: TC-PROJ-005
    Endpoint: GET /api/projects/{project_id}
    Description: Retrieve existing project by ID
    Precondition: Project exists and user owns it
    Input: Valid project_id
    Expected: 200 OK, ProjectResponse
    """
    response = await authenticated_client.get(f"/api/projects/{test_project.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == test_project.id


@pytest.mark.asyncio
async def test_get_project_not_found(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-006
    Endpoint: GET /api/projects/{project_id}
    Description: Request non-existent project
    Input: project_id = 9999
    Expected: 404 Not Found
    """
    response = await authenticated_client.get("/api/projects/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_project_forbidden(authenticated_client, async_db_session, test_project, test_user):
    """
    Test Case: TC-PROJ-007
    Endpoint: GET /api/projects/{project_id}
    Description: User attempts to access another user's project
    Precondition: Project exists but belongs to different user
    Input: Valid project_id owned by another user
    Expected: 403 Forbidden
    """
    other_user = User(
        google_id="987654321",
        email="other@example.com",
        name="Other User",
        is_active=True,
    )
    async_db_session.add(other_user)
    await async_db_session.commit()

    # Create a new client for the other user
    from app.database import get_session
    from app.utils.security import get_current_user_from_cookie

    async def get_test_session():
        yield async_db_session

    async def mock_get_other_user(request=None):
        return {"sub": str(other_user.id), "type": "access"}

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_current_user_from_cookie] = mock_get_other_user

    try:
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as other_client:
            response = await other_client.get(f"/api/projects/{test_project.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_projects_success(authenticated_client, async_db_session, test_user):
    """
    Test Case: TC-PROJ-008
    Endpoint: GET /api/projects/user/{user_id}
    Description: Retrieve all projects for authenticated user
    Precondition: User has multiple projects
    Input: Valid user_id
    Expected: 200 OK, list of ProjectResponse
    """
    # Create multiple projects
    project1 = Project(
        file_id="file_1", user_id=test_user.id, title="Project 1",
        project_url="url1", thumbnail_url="thumb1", width=1920, height=1080, file_type="image"
    )
    project2 = Project(
        file_id="file_2", user_id=test_user.id, title="Project 2",
        project_url="url2", thumbnail_url="thumb2", width=1280, height=720, file_type="video"
    )
    async_db_session.add(project1)
    async_db_session.add(project2)
    await async_db_session.commit()

    response = await authenticated_client.get(f"/api/projects/user/{test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 2


@pytest.mark.asyncio
async def test_get_user_projects_forbidden(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-009
    Endpoint: GET /api/projects/user/{user_id}
    Description: User attempts to access another user's projects
    Input: user_id belonging to different user
    Expected: 403 Forbidden
    """
    response = await authenticated_client.get(f"/api/projects/user/9999")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_project_success(authenticated_client, test_project, test_user):
    """
    Test Case: TC-PROJ-010
    Endpoint: PUT /api/projects/{project_id}
    Description: Update existing project with new data
    Precondition: User owns the project
    Input: UpdateProjectRequest with new title and width
    Expected: 200 OK, updated ProjectResponse
    """
    update_data = {
        "title": "Updated Title",
        "width": 2560,
    }

    with patch("app.routers.project.rename_image_in_imagekit", new_callable=AsyncMock) as mock_rename:
        mock_rename.return_value = {"url": "new_url", "thumbnail": "new_thumb"}
        response = await authenticated_client.put(f"/api/projects/{test_project.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["width"] == 2560


@pytest.mark.asyncio
async def test_patch_update_project_success(authenticated_client, test_project, test_user):
    """
    Test Case: TC-PROJ-011
    Endpoint: PATCH /api/projects/{project_id}
    Description: Partial update using PATCH method
    Precondition: User owns the project
    Input: UpdateProjectRequest with single field (height)
    Expected: 200 OK, only height changed
    """
    update_data = {"height": 2160}

    response = await authenticated_client.patch(f"/api/projects/{test_project.id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["height"] == 2160


@pytest.mark.asyncio
async def test_update_project_not_found(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-012
    Endpoint: PUT /api/projects/{project_id}
    Description: Update non-existent project
    Input: project_id = 9999
    Expected: 404 Not Found
    """
    update_data = {"title": "New Title"}

    response = await authenticated_client.put("/api/projects/9999", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project_forbidden(client_with_db, async_db_session, test_project, test_user):
    """
    Test Case: TC-PROJ-013
    Endpoint: PUT /api/projects/{project_id}
    Description: Non-owner attempts to update project
    Input: Valid project_id, different user_id
    Expected: 403 Forbidden
    """
    other_user = User(
        google_id="987654321",
        email="other@example.com",
        name="Other User",
        is_active=True,
    )
    async_db_session.add(other_user)
    await async_db_session.commit()

    update_data = {"title": "Hacked Title"}

    # Create a new client for the other user
    from app.database import get_session
    from app.utils.security import get_current_user_from_cookie

    async def get_test_session():
        yield async_db_session

    async def mock_get_other_user(request=None):
        return {"sub": str(other_user.id), "type": "access"}

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_current_user_from_cookie] = mock_get_other_user

    try:
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as other_client:
            response = await other_client.put(f"/api/projects/{test_project.id}", json=update_data)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_project_success(authenticated_client, test_project, test_user):
    """
    Test Case: TC-PROJ-014
    Endpoint: DELETE /api/projects/{file_id}
    Description: Delete existing project owned by user
    Precondition: Project exists and user owns it
    Input: Valid file_id
    Expected: 204 No Content
    """
    with patch("app.routers.project.delete_image_from_imagekit", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        response = await authenticated_client.delete(f"/api/projects/{test_project.file_id}")

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_project_not_found(authenticated_client, test_user):
    """
    Test Case: TC-PROJ-015
    Endpoint: DELETE /api/projects/{file_id}
    Description: Delete non-existent project
    Input: file_id = 'nonexistent'
    Expected: 404 Not Found
    """
    response = await authenticated_client.delete("/api/projects/nonexistent")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_forbidden(client_with_db, async_db_session, test_project, test_user):
    """
    Test Case: TC-PROJ-016
    Endpoint: DELETE /api/projects/{file_id}
    Description: Non-owner attempts to delete project
    Input: Valid file_id owned by another user
    Expected: 403 Forbidden
    """
    other_user = User(
        google_id="987654321",
        email="other@example.com",
        name="Other User",
        is_active=True,
    )
    async_db_session.add(other_user)
    await async_db_session.commit()

    # Create a new client for the other user
    from app.database import get_session
    from app.utils.security import get_current_user_from_cookie

    async def get_test_session():
        yield async_db_session

    async def mock_get_other_user(request=None):
        return {"sub": str(other_user.id), "type": "access"}

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_current_user_from_cookie] = mock_get_other_user

    try:
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as other_client:
            response = await other_client.delete(f"/api/projects/{test_project.file_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
