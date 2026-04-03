"""
VisionCrafterAI Backend - Root Endpoint Tests

This module tests the root endpoint (GET /) which returns service status.
"""

import pytest


# ============================================================================
# ROOT ENDPOINT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_root_endpoint_success(client_with_db):
    """
    Test Case: TC-ROOT-001
    Endpoint: GET /
    Description: Verify root endpoint returns service status
    Expected: 200 OK, with service name and status
    """
    response = await client_with_db.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "status" in data
    assert data["status"] == "ok"
