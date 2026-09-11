# models.py
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from database import Base

class TaskStatus(str, enum.Enum):
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    DONE = "Done"
    REMOVED = "Removed"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    sprint = Column(String, index=True, nullable=False)
    us_code = Column(String, nullable=False)
    us_name = Column(String, nullable=False)
    task_code = Column(String, unique=True, index=True, nullable=False)
    task_name = Column(String, nullable=False)
    initial_estimate = Column(Float, nullable=False)
    hours_worked = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TO_DO, nullable=False)

class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    name = Column(String, nullable=False)