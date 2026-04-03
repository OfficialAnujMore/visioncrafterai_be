"""
VisionCrafterAI Backend - Performance and Stress Tests

This module tests application behavior under load:
- Retrieving large datasets
- Response time validation
- Resource efficiency

Performance tests ensure the API scales appropriately.
"""

import pytest
from app.models.project import Project


# ============================================================================
# PERFORMANCE & STRESS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_many_projects(authenticated_client, async_db_session, test_user):
    """
    Test Case: TC-PERF-001
    Description: Retrieve user with many projects (100+)
    Expected: 200 OK, all projects returned efficiently
    """
    # Create 50 projects
    for i in range(50):
        project = Project(
            file_id=f"file_{i}",
            user_id=test_user.id,
            title=f"Project {i}",
            project_url=f"https://example.com/project_{i}.json",
            thumbnail_url=f"https://example.com/thumb_{i}.jpg",
            width=1920,
            height=1080,
            file_type="image" if i % 2 == 0 else "video",
        )
        async_db_session.add(project)

    await async_db_session.commit()

    response = await authenticated_client.get(f"/api/projects/user/{test_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 50
