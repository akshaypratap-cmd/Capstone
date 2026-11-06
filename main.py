# Configure logging first
from app.utils.logging_config import setup_logging

setup_logging()


from fastapi import FastAPI

from app.database import engine, Base
from app import models

from app.routers import tasks, auth

from app.errors import register_error_handlers


# Create FastAPI application
app = FastAPI(
    title="Task Manager API",
    description="Task Manager API with Authentication and Redis",
    version="2.0.0"
)


# Register global error handler
register_error_handlers(app)


# Create database tables
# Suitable for development.
# Use Alembic migrations in production.
Base.metadata.create_all(bind=engine)


# Register routers
app.include_router(auth.router)
app.include_router(tasks.router)


# Home endpoint
@app.get("/")
def home():

    return {
        "message": "Task Manager API is running"
    }


# Health check endpoint
@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }