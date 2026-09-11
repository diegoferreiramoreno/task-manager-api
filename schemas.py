# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from models import TaskStatus

class TaskBase(BaseModel):
    sprint: str
    us_code: str
    us_name: str
    task_code: str
    task_name: str
    initial_estimate: float = Field(..., gt=0, description="Estimated hours must be positive")
    hours_worked: float = Field(0.0, ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.TO_DO

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    # All fields optional for PATCH updates
    sprint: Optional[str] = None
    us_code: Optional[str] = None
    us_name: Optional[str] = None
    task_name: Optional[str] = None
    initial_estimate: Optional[float] = None
    hours_worked: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TaskStatus] = None

class TaskResponse(TaskBase):
    id: int

    class Config:
        from_attributes = True

class GapResponse(BaseModel):
    start_date: datetime
    end_date: datetime
    duration_hours: float
    message: str

    model_config = ConfigDict(json_encoders={
        datetime: lambda v: v.isoformat()
    })
    
class HolidayResponse(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    name: str