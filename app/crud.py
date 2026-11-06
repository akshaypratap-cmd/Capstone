from sqlalchemy.orm import Session

from app import models
from app.schemas import TaskCreate, TaskUpdate


# Find user by email
def get_user_by_email(db: Session, email: str):

    return db.query(models.User).filter(
        models.User.email == email
    ).first()


# Create user
def create_user(db: Session, email: str, hashed_password: str):

    user = models.User(
        email=email,
        hashed_password=hashed_password
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


# Create task
def create_task(db: Session, task: TaskCreate, user_id: int):

    new_task = models.Task(
        title=task.title,
        description=task.description,
        user_id=user_id
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task

    except Exception:
        db.rollback()
        raise


# Get all tasks belonging to a user
def get_all_tasks(db: Session, user_id: int):

    return db.query(models.Task).filter(
        models.Task.user_id == user_id
    ).all()


# Get one task belonging to a user
def get_task_by_id(db: Session, task_id: int, user_id: int):

    return db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == user_id
    ).first()


# Full update
def update_task(db: Session, existing_task, task: TaskUpdate):

    try:
        existing_task.title = task.title
        existing_task.description = task.description
        existing_task.completed = task.completed

        db.commit()
        db.refresh(existing_task)

        return existing_task

    except Exception:
        db.rollback()
        raise


# Partial update
def patch_task(db: Session, existing_task, update_data: dict):

    allowed_fields = {
        "title",
        "description",
        "completed"
    }

    try:
        for key, value in update_data.items():

            if key not in allowed_fields:
                continue

            setattr(existing_task, key, value)

        db.commit()
        db.refresh(existing_task)

        return existing_task

    except Exception:
        db.rollback()
        raise


# Delete task
def delete_task(db: Session, existing_task):

    try:
        db.delete(existing_task)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise