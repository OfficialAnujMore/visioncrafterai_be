"""
ImageKit utilities for image upload and deletion
"""

import httpx
import base64
import os


def get_imagekit_auth_header() -> str:
    """
    Generate Basic Auth header for ImageKit API.

    Returns:
        str: Base64 encoded authorization header value
    """
    private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
    if not private_key:
        raise ValueError("IMAGEKIT_PRIVATE_KEY environment variable is not set")

    # ImageKit uses private_key as username with empty password
    # Format: "private_key:"
    credentials = f"{private_key}:"

    # Encode to base64
    encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    return f"Basic {encoded}"


async def delete_image_from_imagekit(file_id: str) -> bool:
    """
    Delete an image from ImageKit using the file ID.

    API Reference: https://imagekit.io/docs/api-reference/digital-asset-management-dam/managing-assets/delete-file

    Args:
        file_id: The unique fileId from ImageKit (stored in your database)

    Returns:
        bool: True if deletion successful

    Raises:
        Exception: If deletion fails
    """
    try:
        if not file_id:
            raise ValueError("file_id is required")

        url = f"https://api.imagekit.io/v1/files/{file_id}"

        headers = {
            "Accept": "application/json",
            "Authorization": get_imagekit_auth_header(),
        }

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)

            # 204 No Content = successful deletion
            if response.status_code == 204:
                print(f"Successfully deleted file from ImageKit: {file_id}")
                return True
            elif response.status_code == 404:
                print(f"File not found in ImageKit: {file_id}")
                # File already deleted or doesn't exist - treat as success
                return True
            else:
                error_detail = response.json() if response.text else "Unknown error"
                raise Exception(
                    f"ImageKit API returned {response.status_code}: {error_detail}"
                )

    except httpx.HTTPError as e:
        raise Exception(f"Failed to delete image from ImageKit: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to delete image from ImageKit: {str(e)}")
