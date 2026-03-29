"""
ImageKit utilities for image upload and deletion
"""

import httpx
import base64
import os
import re


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


def sanitize_file_basename(name: str) -> str:
    """Create a safe basename compatible with ImageKit rename constraints."""
    normalized = name.strip().lower()
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r"[^a-z0-9._-]", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    return normalized or "untitled"


async def get_file_details_from_imagekit(file_id: str) -> dict:
    """
    Fetch current file details from ImageKit.

    Args:
        file_id: ImageKit file ID.

    Returns:
        dict: File details payload from ImageKit.
    """
    if not file_id:
        raise ValueError("file_id is required")

    url = f"https://api.imagekit.io/v1/files/{file_id}/details"
    headers = {
        "Accept": "application/json",
        "Authorization": get_imagekit_auth_header(),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        error_detail = response.text or "Unknown error"
        raise Exception(
            f"Failed to fetch file details from ImageKit ({response.status_code}): {error_detail}"
        )

    return response.json()


async def rename_image_in_imagekit(file_id: str, new_title: str) -> dict:
    """
    Rename an existing ImageKit file based on project title and return updated file details.

    Args:
        file_id: ImageKit file ID.
        new_title: New project title used as file basename.

    Returns:
        dict: Updated ImageKit file details.
    """
    file_details = await get_file_details_from_imagekit(file_id)

    current_name = file_details.get("name", "")
    file_path = file_details.get("filePath")

    if not file_path:
        raise Exception("ImageKit filePath missing in file details response")

    extension = ""
    if "." in current_name:
        extension = current_name[current_name.rfind("."):]

    new_basename = sanitize_file_basename(new_title)
    new_file_name = f"{new_basename}{extension}"

    # Skip rename call if generated name matches current name.
    if new_file_name == current_name:
        return file_details

    rename_url = "https://api.imagekit.io/v1/files/rename"
    headers = {
        "Accept": "application/json",
        "Authorization": get_imagekit_auth_header(),
        "Content-Type": "application/json",
    }
    payload = {
        "filePath": file_path,
        "newFileName": new_file_name,
        "purgeCache": True,
    }

    async with httpx.AsyncClient() as client:
        rename_response = await client.put(rename_url, headers=headers, json=payload)

    if rename_response.status_code not in (200, 207):
        error_detail = rename_response.text or "Unknown error"
        raise Exception(
            f"Failed to rename file in ImageKit ({rename_response.status_code}): {error_detail}"
        )

    # Read details again to get updated URL and thumbnail.
    return await get_file_details_from_imagekit(file_id)


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
