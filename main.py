# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import engine, get_db
from datetime import datetime, time
from gap_service import GapAnalyzer, BrasilApiHolidayProvider, HolidayFromDBProvider
import pytz

TZ_BR = pytz.timezone("America/Sao_Paulo")
TZ_UTC = pytz.utc

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API")

# --- Tasks Endpoints ---

@app.post("/tasks", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task in the database.
    """
    # Check if task_code already exists
    existing_task = db.query(models.Task).filter(models.Task.task_code == task.task_code).first()
    if existing_task:
        raise HTTPException(status_code=400, detail="Task code already exists")

    # Mapping Pydantic schema to SQLAlchemy model
    db_task = models.Task(**task.model_dump())
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[schemas.TaskResponse])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all tasks with pagination support.
    """
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks

#get para obter uma lista de tarefas por período de start_date ordenadas por start_date
@app.get("/tasks/by_start_date", response_model=List[schemas.TaskResponse])
def read_tasks_by_start_date(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """
    Retrieve tasks within a specific start_date range, ordered by start_date.
    """
    print(f"Fetching tasks from {start_date} to {end_date}")
    tasks = db.query(models.Task).filter(
        models.Task.start_date >= start_date,
        models.Task.start_date <= end_date
    ).order_by(models.Task.start_date).all()
    return tasks

#get para obter o somatorio de hours_worked no período de start_date
@app.get("/tasks/total_hours_worked")
def get_total_hours_worked(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """
    Retrieve the total hours worked within a specific start_date range.
    """
    total_hours = db.query(models.Task).filter(
        models.Task.start_date >= start_date,
        models.Task.start_date <= end_date
    ).with_entities(func.sum(models.Task.hours_worked)).scalar()
    return {"total_hours_worked": total_hours or 0}

#get para obter o somatorio de hours_worked por sprint deve ser case insensitive
@app.get("/tasks/total_hours_worked_by_sprint")
def get_total_hours_worked_by_sprint(sprint: str, db: Session = Depends(get_db)):
    """
    Retrieve the total hours worked for a specific sprint (case insensitive).
    """
    total_hours = db.query(models.Task).filter(
        func.lower(models.Task.sprint) == sprint.lower()
    ).with_entities(func.sum(models.Task.hours_worked)).scalar()
    return {"total_hours_worked": total_hours or 0}

#get para obter o somatorio de hours_worked por mes e ano
@app.get("/tasks/total_hours_worked_by_month_year")
def get_total_hours_worked_by_month_year(month: int, year: int, db: Session = Depends(get_db)):
    """
    Retrieve the total hours worked for a specific month and year.
    """
    total_hours = db.query(models.Task).filter(
        func.extract('month', models.Task.start_date) == month,
        func.extract('year', models.Task.start_date) == year
    ).with_entities(func.sum(models.Task.hours_worked)).scalar()
    return {"total_hours_worked": total_hours or 0}

@app.get("/tasks/code/{task_code}", response_model=schemas.TaskResponse)
def read_task_by_code(task_code: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific task by task_code.
    """
    task = db.query(models.Task).filter(models.Task.task_code == task_code).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific task by ID.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Update an existing task.
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    for key, value in task_update.model_dump().items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task.
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return None

@app.post("/tasks/upsert", response_model=schemas.TaskResponse)
def upsert_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Upsert a task in the database.
    If the task with the given task_code exists, update it; otherwise, create a new one.
    """
    db_task = db.query(models.Task).filter(models.Task.task_code == task.task_code).first()
    
    task_map = task.model_dump()

    if db_task:
        # Update existing task
        for key, value in task_map.items():
            setattr(db_task, key, value)
        db.commit()
        db.refresh(db_task)
        return db_task
    else:
        # Create new task
        new_task = models.Task(**task_map)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

@app.get("/gaps", response_model=List[schemas.GapResponse])
def get_activity_gaps(
    start_date: datetime, 
    end_date: datetime, 
    db: Session = Depends(get_db)
):
    """
    Identify gaps between activities within a specific range.
    Ignores weekends and tasks without complete dates.
    """

    raw_start_date = start_date.date()
    raw_end_date = end_date.date()
    start_br = TZ_BR.localize(datetime.combine(raw_start_date, time.min))
    end_br = TZ_BR.localize(datetime.combine(raw_end_date, time.max))
    start_query_utc = start_br.astimezone(TZ_UTC)
    end_query_utc = end_br.astimezone(TZ_UTC)
    start_query_naive = start_query_utc.replace(tzinfo=None)
    end_query_naive = end_query_utc.replace(tzinfo=None)
    # 1. Fetch valid tasks in range
    # We fetch tasks that overlap with the query range
    tasks = db.query(models.Task).filter(
        models.Task.start_date != None,
        models.Task.end_date != None,
        models.Task.end_date >= start_query_naive,
        models.Task.start_date <= end_query_naive
    ).order_by(models.Task.start_date).all()

    for task in tasks:
        if task.start_date:
            task.start_date = TZ_UTC.localize(task.start_date).astimezone(TZ_BR)
        if task.end_date:
            task.end_date = TZ_UTC.localize(task.end_date).astimezone(TZ_BR)

    # 2. Instantiate Service (Dependency Injection could be more formal, but this works)
    holiday_provider = BrasilApiHolidayProvider()
    holiday_db_provider = HolidayFromDBProvider(db)
    analyzer = GapAnalyzer(holiday_provider, holiday_db_provider)

    # 3. Calculate
    gaps = analyzer.calculate_gaps(start_br, end_br, tasks)
    
    return gaps

# --- Holidays Endpoints ---
@app.post("/holidays", response_model=schemas.HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(holiday: schemas.HolidayResponse, db: Session = Depends(get_db)):
    """
    Create a new holiday in the database.
    """
    db_holiday = models.Holiday(**holiday.model_dump())
    
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

@app.get("/holidays", response_model=List[schemas.HolidayResponse])
def read_holidays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all holidays with pagination support.
    """
    holidays = db.query(models.Holiday).offset(skip).limit(limit).all()
    return holidays

@app.put("/holidays/{holiday_id}", response_model=schemas.HolidayResponse)
def update_holiday(holiday_id: int, holiday_update: schemas.HolidayResponse, db: Session = Depends(get_db)):
    """
    Update an existing holiday.
    """
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if db_holiday is None:
        raise HTTPException(status_code=404, detail="Holiday not found")

    # Update fields
    for key, value in holiday_update.model_dump().items():
        setattr(db_holiday, key, value)

    db.commit()
    db.refresh(db_holiday)
    return db_holiday

@app.delete("/holidays/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    """
    Delete a holiday.
    """
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if db_holiday is None:
        raise HTTPException(status_code=404, detail="Holiday not found")

    db.delete(db_holiday)
    db.commit()
    return None

# Is this date holiday? (BrazilAPI + DB)
@app.get("/holidays/is_holiday")
def is_holiday(date: datetime, db: Session = Depends(get_db)):
    """
    Check if a given date is a holiday using both BrasilAPI and local DB.
    """
    holiday_provider = BrasilApiHolidayProvider()
    holiday_db_provider = HolidayFromDBProvider(db)

    is_holiday_api = holiday_provider.is_holiday(date)
    is_holiday_db = holiday_db_provider.is_holiday(date)

    return {
        "date": date,
        "is_holiday_api": is_holiday_api,
        "is_holiday_db": is_holiday_db,
        "is_holiday": is_holiday_api or is_holiday_db
    }

@app.get("/holidays/{holiday_id}", response_model=schemas.HolidayResponse)
def read_holiday(holiday_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a holiday by its ID.
    """
    db_holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if db_holiday is None:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return db_holiday