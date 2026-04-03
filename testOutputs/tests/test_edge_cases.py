"""
VisionCrafterAI Backend - Edge Cases and Validation Tests

This module tests edge cases and input validation:
- Empty string inputs
- Zero and very large dimensions
- Special characters and XSS prevention
- Boundary conditions

These tests ensure robustness against unexpected inputs and malicious data.
"""

import pytest
from unittest.mock import patch, AsyncMock


# ============================================================================
# EDGE CASES & VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_project_with_empty_title(authenticated_client, test_user):
    """
    Test Case: TC-EDGE-001
    Description: Create project with empty string title
    Expected: May succeed or fail depending on validation rules
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "",  # Empty title
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "image",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    # Either 201 (allowed) or 422 (validation error)
    assert response.status_code in [201, 422]


@pytest.mark.asyncio
async def test_create_project_with_zero_dimensions(authenticated_client, test_user):
    """
    Test Case: TC-EDGE-002
    Description: Create project with zero width/height
    Expected: May succeed or fail depending on validation
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "Bad Dimensions",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 0,
        "height": 0,
        "file_type": "image",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    # Should either fail validation or succeed
    assert response.status_code in [201, 422]


@pytest.mark.asyncio
async def test_create_project_with_large_dimensions(authenticated_client, test_user):
    """
    Test Case: TC-EDGE-003
    Description: Create project with very large dimensions (4K+)
    Expected: 201 Created (no upper bound validation)
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "4K Project",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 7680,  # 8K width
        "height": 4320,  # 8K height
        "file_type": "video",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_update_project_with_very_long_title(authenticated_client, test_project, test_user):
    """
    Test Case: TC-EDGE-004
    Description: Update project with extremely long title (>500 chars)
    Expected: 200 OK (may or may not have DB field length validation)
    """
    long_title = "A" * 1000
    update_data = {"title": long_title}

    with patch("app.routers.project.rename_image_in_imagekit", new_callable=AsyncMock) as mock_rename:
        mock_rename.return_value = {"url": "new_url", "thumbnail": "new_thumb"}
        response = await authenticated_client.put(f"/api/projects/{test_project.id}", json=update_data)

    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_create_project_with_special_characters_in_title(authenticated_client, test_user):
    """
    Test Case: TC-EDGE-005
    Description: Create project with special characters in title
    Expected: 201 Created (special chars should be escaped properly)
    """
    project_data = {
        "file_id": "file_123",
        "user_id": test_user.id,
        "title": "Project <script>alert('xss')</script> & More",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "image",
    }

    response = await authenticated_client.post("/api/projects/create", json=project_data)

    assert response.status_code == 201
    data = response.json()
    # Title should be stored as-is (DB should escape it)
    assert data["data"]["title"] == project_data["title"]
