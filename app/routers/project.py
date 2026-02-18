from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone
import json

from app.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
from app.schemas.common import ApiResponse
from app.models.project import Project
from app.database import get_session
from app.utils.security import get_current_user_from_cookie
from app.utils.imagekit import delete_image_from_imagekit
from sqlalchemy import delete

router = APIRouter(prefix="/api/projects", tags=["Projects"])


def serialize_project(project: Project) -> ProjectResponse:
    """Helper function to serialize a Project model to ProjectResponse"""
    canvas_state_dict = None
    if project.canvas_state:
        try:
            canvas_state_dict = json.loads(project.canvas_state)
        except (json.JSONDecodeError, TypeError):
            canvas_state_dict = None
    
    return ProjectResponse(
        id=project.id,
        file_id=project.file_id,
        user_id=project.user_id,
        title=project.title,
        project_url=project.project_url,
        thumbnail_url=project.thumbnail_url,
        width=project.width,
        height=project.height,
        file_type=project.file_type,
        canvas_state=canvas_state_dict,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post(
    "/create",
    response_model=ApiResponse[ProjectResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project_data: CreateProjectRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_from_cookie),
) -> ApiResponse[ProjectResponse]:
    """
    Create a new project.

    Args:
        project_data: Contains user_id, title, project_url, thumbnail_url, width, height, file_type
        session: Database session (FastAPI provides automatically)

    Returns:
        ProjectResponse: The created project

    Raises:
        HTTPException 500: If project creation fails
    """
    user_id = int(current_user.get("sub"))
    
    canvas_state_json = None
    if project_data.canvas_state is not None:
        canvas_state_json = json.dumps(project_data.canvas_state)
    
    db_project = Project(
        file_id=project_data.file_id,
        user_id=user_id,
        title=project_data.title,
        project_url=project_data.project_url,
        thumbnail_url=project_data.thumbnail_url,
        width=project_data.width,
        height=project_data.height,
        file_type=project_data.file_type,
        canvas_state=canvas_state_json,
    )

    try:
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)

        project_response = serialize_project(db_project)

        return ApiResponse(
            success=True, message="Project created successfully", data=project_response
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}",
        )


@router.get("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def get_project(
    project_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_from_cookie),
) -> ApiResponse[ProjectResponse]:
    """
    Get a project by ID.

    Args:
        project_id: The ID of the project to retrieve
        session: Database session

    Returns:
        ProjectResponse: The requested project

    Raises:
        HTTPException 404: If project not found
    """
    current_user_id = int(current_user.get("sub"))
    
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    if project.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this project",
        )

    return ApiResponse(
        success=True,
        data=serialize_project(project),
    )


@router.get("/user/{user_id}", response_model=ApiResponse[list[ProjectResponse]])
async def get_user_projects(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_from_cookie),
) -> ApiResponse[list[ProjectResponse]]:
    """
    Get all projects for a specific user.

    Args:
        user_id: The ID of the user
        session: Database session
        current_user: Current authenticated user from JWT

    Returns:
        list[ProjectResponse]: List of projects belonging to the user
    """
    current_user_id = int(current_user.get("sub"))
    
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own projects",
        )
    
    statement = (
        select(Project)
        .where(Project.user_id == current_user_id)
        .order_by(Project.created_at.desc())
    )
    result = await session.execute(statement)
    projects = result.scalars().all()

    projects_list = [serialize_project(project) for project in projects]

    return ApiResponse(success=True, data=projects_list)


@router.put("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def update_project(
    project_id: int,
    project_data: UpdateProjectRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_from_cookie),
) -> ApiResponse[ProjectResponse]:
    """
    Update an existing project.

    Args:
        project_id: The ID of the project to update
        project_data: Fields to update
        session: Database session
        current_user: Current authenticated user from JWT

    Returns:
        ProjectResponse: The updated project

    Raises:
        HTTPException 404: If project not found
        HTTPException 403: If user is not authorized to update the project
    """
    current_user_id = int(current_user.get("sub"))
    
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    if project.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this project",
        )

    # Update only provided fields
    if project_data.title is not None:
        project.title = project_data.title
    if project_data.project_url is not None:
        project.project_url = project_data.project_url
    if project_data.thumbnail_url is not None:
        project.thumbnail_url = project_data.thumbnail_url
    if project_data.width is not None:
        project.width = project_data.width
    if project_data.height is not None:
        project.height = project_data.height
    if project_data.file_type is not None:
        project.file_type = project_data.file_type
    if project_data.canvas_state is not None:
        project.canvas_state = json.dumps(project_data.canvas_state)

    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        project_response = serialize_project(project)

        return ApiResponse(
            success=True, message="Project updated successfully", data=project_response
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}",
        )


@router.patch("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def patch_update_project(
    project_id: int,
    project_data: UpdateProjectRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_from_cookie),
) -> ApiResponse[ProjectResponse]:
    """
    Partially update an existing project (PATCH).

    Args:
        project_id: The ID of the project to update
        project_data: Fields to update
        session: Database session
        current_user: Current authenticated user from JWT

    Returns:
        ProjectResponse: The updated project

    Raises:
        HTTPException 404: If project not found
        HTTPException 403: If user is not authorized to update the project
    """
    current_user_id = int(current_user.get("sub"))
    
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    
    if project.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this project",
        )

    # Update only provided fields
    if project_data.title is not None:
        project.title = project_data.title
    if project_data.project_url is not None:
        project.project_url = project_data.project_url
    if project_data.thumbnail_url is not None:
        project.thumbnail_url = project_data.thumbnail_url
    if project_data.width is not None:
        project.width = project_data.width
    if project_data.height is not None:
        project.height = project_data.height
    if project_data.file_type is not None:
        project.file_type = project_data.file_type
    if project_data.canvas_state is not None:
        project.canvas_state = json.dumps(project_data.canvas_state)

    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        project_response = serialize_project(project)

        return ApiResponse(
            success=True, message="Project updated successfully", data=project_response
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}",
        )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    file_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_from_cookie),
) -> None:
    """
    Delete a project by file_id.

    Steps:
    1. Find the project by file_id and ensure it exists.
    2. Verify the current user owns the project.
    3. Call ImageKit API to delete the file by file_id.
    4. If ImageKit deletion succeeds, delete the DB row where file_id == file_id.
    """
    statement = select(Project).where(Project.file_id == file_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with file_id {file_id} not found",
        )

    current_user_id = int(current_user.get("sub"))

    if project.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this project",
        )

    try:
        # Delete on ImageKit first (delete_image_from_imagekit raises on error)
        await delete_image_from_imagekit(file_id)

        # If ImageKit deletion succeeded, delete DB row using where(file_id == file_id)
        delete_stmt = delete(Project).where(Project.file_id == file_id)
        await session.execute(delete_stmt)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}",
        )
