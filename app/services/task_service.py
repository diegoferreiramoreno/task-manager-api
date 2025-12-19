"""Task service for business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Service class for Task operations following SOLID principles."""
    
    @staticmethod
    def create_task(db: Session, task_data: TaskCreate) -> Task:
        """
        Create a new task.
        
        Args:
            db: Database session
            task_data: Task creation data
            
        Returns:
            Task: Created task
        """
        task = Task(**task_data.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        return db.query(Task).filter(Task.id == task_id).first()
    
    @staticmethod
    def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get list of tasks with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List[Task]: List of tasks
        """
        return db.query(Task).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """
        Update a task.
        
        Args:
            db: Database session
            task_id: Task ID
            task_data: Task update data
            
        Returns:
            Optional[Task]: Updated task if found, None otherwise
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            db: Database session
            task_id: Task ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True
