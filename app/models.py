from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    false,
    func
)
from sqlalchemy.orm import relationship

from app.database import Base


# User database table
class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # One user can have multiple tasks
    tasks = relationship(
        "Task",
        back_populates="owner"
    )


# Task database table
class Task(Base):

    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=True
    )

    completed = Column(
        Boolean,
        default=False,
        server_default=false(),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Each task belongs to one user
    owner = relationship(
        "User",
        back_populates="tasks"
    )