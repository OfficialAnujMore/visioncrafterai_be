"""
VisionCrafterAI Backend - Integration Tests

This module tests end-to-end workflows across multiple endpoints:
- Complete project lifecycle (create → update → delete)
- Multi-step operations and state transitions

Integration tests verify that components work correctly together.
"""

import pytest
from unittest.mock import patch, AsyncMock


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_workflow_create_update_delete(authenticated_client, test_user):
    """
    Test Case: TC-INT-001
    Description: Full workflow - create project, update it, then delete it
    Expected: All operations succeed with proper state transitions
    """
    # Step 1: Create project
    create_data = {
        "file_id": "workflow_file_123",
        "user_id": test_user.id,
        "title": "Workflow Project",
        "project_url": "https://example.com/project.json",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "width": 1920,
        "height": 1080,
        "file_type": "image",
    }

    create_response = await authenticated_client.post("/api/projects/create", json=create_data)

    assert create_response.status_code == 201
    project_id = create_response.json()["data"]["id"]

    # Step 2: Update project
    update_data = {"title": "Updated Workflow Project"}

    with patch("app.routers.project.rename_image_in_imagekit", new_callable=AsyncMock) as mock_rename:
        mock_rename.return_value = {"url": "new_url", "thumbnail": "new_thumb"}
        update_response = await authenticated_client.put(f"/api/projects/{project_id}", json=update_data)

    assert update_response.status_code == 200

    # Step 3: Delete project
    with patch("app.routers.project.delete_image_from_imagekit", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = None
        delete_response = await authenticated_client.delete(f"/api/projects/workflow_file_123")

    assert delete_response.status_code == 204
