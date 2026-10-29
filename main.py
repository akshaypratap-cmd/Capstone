
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, SessionLocal
from app import models
from app.schemas import TaskCreate, TaskUpdate, TaskPatch

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = models.Task(
        title=task.title,
        description=task.description
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks



@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db)
):
    existing_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if existing_task is None:
        return {"message": "Task not found"}

    existing_task.title = task.title
    existing_task.description = task.description
    existing_task.completed = task.completed

    db.commit()
    db.refresh(existing_task)

    return existing_task


@app.patch("/tasks/{task_id}")
def patch_task(
    task_id: int,
    task: TaskPatch,
    db: Session = Depends(get_db)
):
    existing_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if existing_task is None:
        return {"message": "Task not found"}

    update_data = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_task, key, value)

    db.commit()
    db.refresh(existing_task)

    return existing_task



@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    existing_task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if existing_task is None:
        return {"message": "Task not found"}

    db.delete(existing_task)
    db.commit()

    return {"message": "Task deleted successfully"}
