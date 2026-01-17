from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from app.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
from app.schemas.common import ApiResponse
from app.models.project import Project
from app.database import get_session

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("/create", response_model=ApiResponse[ProjectResponse], status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: CreateProjectRequest,
    session: AsyncSession = Depends(get_session)
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
    db_project = Project(
        user_id=project_data.user_id,
        title=project_data.title,
        project_url=project_data.project_url,
        thumbnail_url=project_data.thumbnail_url,
        width=project_data.width,
        height=project_data.height,
        file_type=project_data.file_type,
    )

    try:
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)

        project_response = ProjectResponse(
            id=db_project.id,
            user_id=db_project.user_id,
            title=db_project.title,
            project_url=db_project.project_url,
            thumbnail_url=db_project.thumbnail_url,
            width=db_project.width,
            height=db_project.height,
            file_type=db_project.file_type,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at,
        )

        return ApiResponse(
            success=True,
            message="Project created successfully",
            data=project_response
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
    session: AsyncSession = Depends(get_session)
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
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    return ApiResponse(
        success=True,
        data=ProjectResponse(
            id=project.id,
            user_id=project.user_id,
            title=project.title,
            project_url=project.project_url,
            thumbnail_url=project.thumbnail_url,
            width=project.width,
            height=project.height,
            file_type=project.file_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
    )


@router.get("/user/{user_id}", response_model=ApiResponse[list[ProjectResponse]])
async def get_user_projects(
    user_id: int,
    session: AsyncSession = Depends(get_session)
) -> ApiResponse[list[ProjectResponse]]:
    """
    Get all projects for a specific user.

    Args:
        user_id: The ID of the user
        session: Database session

    Returns:
        list[ProjectResponse]: List of projects belonging to the user
    """
    statement = select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
    result = await session.execute(statement)
    projects = result.scalars().all()

    projects_list = [
        ProjectResponse(
            id=project.id,
            user_id=project.user_id,
            title=project.title,
            project_url=project.project_url,
            thumbnail_url=project.thumbnail_url,
            width=project.width,
            height=project.height,
            file_type=project.file_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
        for project in projects
    ]

    return ApiResponse(
        success=True,
        data=projects_list
    )


@router.put("/{project_id}", response_model=ApiResponse[ProjectResponse])
async def update_project(
    project_id: int,
    project_data: UpdateProjectRequest,
    session: AsyncSession = Depends(get_session)
) -> ApiResponse[ProjectResponse]:
    """
    Update an existing project.

    Args:
        project_id: The ID of the project to update
        project_data: Fields to update
        session: Database session

    Returns:
        ProjectResponse: The updated project

    Raises:
        HTTPException 404: If project not found
    """
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
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

    project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        project_response = ProjectResponse(
            id=project.id,
            user_id=project.user_id,
            title=project.title,
            project_url=project.project_url,
            thumbnail_url=project.thumbnail_url,
            width=project.width,
            height=project.height,
            file_type=project.file_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

        return ApiResponse(
            success=True,
            message="Project updated successfully",
            data=project_response
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}",
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Delete a project.

    Args:
        project_id: The ID of the project to delete
        session: Database session

    Raises:
        HTTPException 404: If project not found
    """
    statement = select(Project).where(Project.id == project_id)
    result = await session.execute(statement)
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    try:
        await session.delete(project)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}",
        )
