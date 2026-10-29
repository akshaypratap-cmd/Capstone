
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    completed: bool


class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
