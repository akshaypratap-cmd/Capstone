from fastapi import (
    APIRouter,
    Depends,
    Path,
    status
)

from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    get_current_user
)

from app.models import User

from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    TaskResponse
)

from app.services import task_service


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# CREATE TASK
@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return task_service.create_new_task(
        db,
        task,
        current_user.id
    )


# GET ALL TASKS
@router.get(
    "/",
    response_model=list[TaskResponse]
)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return task_service.get_tasks(
        db,
        current_user.id
    )


# GET TASK BY ID
@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return task_service.get_single_task(
        db,
        task_id,
        current_user.id
    )


# PUT - FULL UPDATE
@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task: TaskUpdate,
    task_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return task_service.update_existing_task(
        db,
        task_id,
        task,
        current_user.id
    )


# PATCH - PARTIAL UPDATE
@router.patch(
    "/{task_id}",
    response_model=TaskResponse
)
def patch_task(
    task: TaskPatch,
    task_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    update_data = task.model_dump(
        exclude_unset=True
    )

    return task_service.patch_existing_task(
        db,
        task_id,
        update_data,
        current_user.id
    )


# DELETE TASK
@router.delete(
    "/{task_id}"
)
def delete_task(
    task_id: int = Path(gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return task_service.remove_task(
        db,
        task_id,
        current_user.id
    )