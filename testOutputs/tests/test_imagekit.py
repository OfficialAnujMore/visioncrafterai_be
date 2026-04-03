"""
VisionCrafterAI Backend - ImageKit Integration Tests

This module tests ImageKit integration endpoints:
- Generate authentication parameters for client-side uploads
- Error handling for unauthorized requests

ImageKit is used for file management (images and video thumbnails).
"""

import pytest
from unittest.mock import patch


# ============================================================================
# IMAGEKIT ENDPOINTS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_imagekit_auth_success(authenticated_client, test_user):
    """
    Test Case: TC-IMK-001
    Endpoint: GET /api/imagekit/auth
    Description: Generate ImageKit authentication parameters
    Precondition: User is authenticated
    Expected: 200 OK, ImageKitAuthResponse with token, expire, signature
    """
    with patch("app.routers.imagekit.imagekit.helper.get_authentication_parameters") as mock_auth:
        mock_auth.return_value = {
            "token": "test_token_123",
            "expire": 1735689600,
            "signature": "test_signature",
        }
        response = await authenticated_client.get("/api/imagekit/auth")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data["data"]
    assert "expire" in data["data"]
    assert "signature" in data["data"]


@pytest.mark.asyncio
async def test_get_imagekit_auth_unauthorized(client_with_db):
    """
    Test Case: TC-IMK-002
    Endpoint: GET /api/imagekit/auth
    Description: ImageKit auth without authentication token
    Input: No JWT token in cookies
    Expected: 401 Unauthorized
    """
    # client_with_db doesn't have authenticated user, so this should return 401
    response = await client_with_db.get("/api/imagekit/auth")

    assert response.status_code == 401
