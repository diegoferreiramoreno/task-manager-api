"""Task API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task.
    
    Args:
        task_data: Task creation data
        db: Database session
        
    Returns:
        TaskResponse: Created task
    """
    return TaskService.create_task(db, task_data)


@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Get all tasks"
)
def get_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """
    Get list of all tasks with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List[TaskResponse]: List of tasks
    """
    return TaskService.get_tasks(db, skip, limit)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID"
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Get a specific task by ID.
    
    Args:
        task_id: Task ID
        db: Database session
        
    Returns:
        TaskResponse: Task details
        
    Raises:
        HTTPException: 404 if task not found
    """
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Update task"
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """
    Update an existing task.
    
    Args:
        task_id: Task ID
        task_data: Task update data
        db: Database session
        
    Returns:
        TaskResponse: Updated task
        
    Raises:
        HTTPException: 404 if task not found
    """
    task = TaskService.update_task(db, task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task"
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a task.
    
    Args:
        task_id: Task ID
        db: Database session
        
    Raises:
        HTTPException: 404 if task not found
    """
    deleted = TaskService.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
