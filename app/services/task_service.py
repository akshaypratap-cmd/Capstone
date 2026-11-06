from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import crud

from app.schemas import TaskCreate, TaskUpdate

from app.redis_cache import (
    get_cache,
    set_cache,
    delete_cache
)


# Generate cache key for a user's tasks
def get_tasks_cache_key(user_id: int) -> str:

    return f"tasks:user:{user_id}"


# Create task
def create_new_task(
    db: Session,
    task: TaskCreate,
    user_id: int
):

    new_task = crud.create_task(
        db,
        task,
        user_id
    )

    delete_cache(get_tasks_cache_key(user_id))

    return new_task


# Get all tasks
def get_tasks(db: Session, user_id: int):

    cache_key = get_tasks_cache_key(user_id)

    # Check Redis cache first
    cached_tasks = get_cache(cache_key)

    if cached_tasks is not None:
        return cached_tasks

    # Fetch tasks from database
    tasks = crud.get_all_tasks(db, user_id)

    # Convert database objects into dictionaries
    result = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "user_id": task.user_id
        }
        for task in tasks
    ]

    # Store results in Redis for 60 seconds
    set_cache(
        cache_key,
        result,
        expire=60
    )

    return result


# Get one task
def get_single_task(
    db: Session,
    task_id: int,
    user_id: int
):

    task = crud.get_task_by_id(
        db,
        task_id,
        user_id
    )

    if task is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# Full update
def update_existing_task(
    db: Session,
    task_id: int,
    task: TaskUpdate,
    user_id: int
):

    existing_task = get_single_task(
        db,
        task_id,
        user_id
    )

    updated_task = crud.update_task(
        db,
        existing_task,
        task
    )

    delete_cache(get_tasks_cache_key(user_id))

    return updated_task


# Partial update
def patch_existing_task(
    db: Session,
    task_id: int,
    update_data: dict[str, Any],
    user_id: int
):

    existing_task = get_single_task(
        db,
        task_id,
        user_id
    )

    updated_task = crud.patch_task(
        db,
        existing_task,
        update_data
    )

    delete_cache(get_tasks_cache_key(user_id))

    return updated_task


# Delete task
def remove_task(
    db: Session,
    task_id: int,
    user_id: int
):

    existing_task = get_single_task(
        db,
        task_id,
        user_id
    )

    crud.delete_task(
        db,
        existing_task
    )

    delete_cache(get_tasks_cache_key(user_id))

    return {
        "message": "Task deleted successfully"
    }