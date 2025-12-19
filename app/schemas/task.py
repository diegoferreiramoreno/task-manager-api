"""Task schemas for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    """Base schema for Task with common attributes."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(False, description="Task completion status")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: Optional[bool] = Field(None, description="Task completion status")


class TaskResponse(TaskBase):
    """Schema for task response."""
    
    id: int = Field(..., description="Task ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)
