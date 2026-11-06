import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.database import Base
from app.dependencies import get_db

from main import app


# Separate in-memory database for testing
TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# Create and clean up test database
@pytest.fixture
def db():

    Base.metadata.create_all(bind=test_engine)

    database = TestingSessionLocal()

    try:
        yield database

    finally:
        database.close()
        Base.metadata.drop_all(bind=test_engine)


# Override real database dependency
@pytest.fixture
def client(db):

    def override_get_db():

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:

        with TestClient(app) as test_client:
            yield test_client

    finally:

        app.dependency_overrides.clear()


# Register a test user and return authentication headers
@pytest.fixture
def auth_headers(client):

    register_response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert register_response.status_code in (200, 201), (
        f"Registration failed: {register_response.text}"
    )

    login_response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200, (
        f"Login failed: {login_response.text}"
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }