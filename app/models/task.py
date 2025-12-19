"""Task model definition."""
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.db.session import Base


class Task(Base):
    """Task model for database."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', completed={self.completed})>"
