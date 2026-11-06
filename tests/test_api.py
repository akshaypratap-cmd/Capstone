# 1. Test home endpoint
def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Task Manager API is running"


# 2. Test health endpoint
def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# 3. Test user registration
def test_register(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"


# 4. Test duplicate registration
def test_duplicate_registration(client):
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123"
    }

    first_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 201

    second_response = client.post("/auth/register", json=user_data)

    assert second_response.status_code == 409


# 5. Test user login
def test_login(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# 6. Test task creation
def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn FastAPI",
            "description": "Practice API development"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Learn FastAPI"
    assert response.json()["completed"] is False


# 7. Test retrieving tasks
def test_get_tasks(client, auth_headers):
    response = client.get(
        "/tasks",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


# 8. Test unauthorized access
def test_unauthorized_access(client):
    response = client.get("/tasks")

    assert response.status_code == 401


# 9. Test task ownership
def test_task_ownership(client):
    # Register first user
    client.post(
        "/auth/register",
        json={
            "email": "user1@example.com",
            "password": "password123"
        }
    )

    # Login first user
    login1 = client.post(
        "/auth/login",
        data={
            "username": "user1@example.com",
            "password": "password123"
        }
    )

    assert login1.status_code == 200

    token1 = login1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # First user creates a task
    task = client.post(
        "/tasks",
        json={
            "title": "Private task",
            "description": "Only user 1 should access this"
        },
        headers=headers1
    )

    assert task.status_code == 201

    task_id = task.json()["id"]

    # Register second user
    client.post(
        "/auth/register",
        json={
            "email": "user2@example.com",
            "password": "password123"
        }
    )

    # Login second user
    login2 = client.post(
        "/auth/login",
        data={
            "username": "user2@example.com",
            "password": "password123"
        }
    )

    assert login2.status_code == 200

    token2 = login2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Second user tries to access first user's task
    response = client.get(
        f"/tasks/{task_id}",
        headers=headers2
    )

    assert response.status_code == 404


# 10. Test task not found
def test_task_not_found(client, auth_headers):
    response = client.get(
        "/tasks/99999",
        headers=auth_headers
    )

    assert response.status_code == 404


# 11. Test task creation without title
def test_create_task_without_title(client, auth_headers):
    response = client.post(
        "/tasks",
        json={
            "description": "Task without a title"
        },
        headers=auth_headers
    )

    assert response.status_code == 422



def test_task_ownership_all_operations(client):
    # Register User A
    client.post(
        "/auth/register",
        json={
            "email": "owner@example.com",
            "password": "password123"
        }
    )

    login_a = client.post(
        "/auth/login",
        data={
            "username": "owner@example.com",
            "password": "password123"
        }
    )

    headers_a = {
        "Authorization": f"Bearer {login_a.json()['access_token']}"
    }

    # User A creates a task
    task = client.post(
        "/tasks",
        json={"title": "Private task"},
        headers=headers_a
    )

    task_id = task.json()["id"]

    # Register User B
    client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "password123"
        }
    )

    login_b = client.post(
        "/auth/login",
        data={
            "username": "other@example.com",
            "password": "password123"
        }
    )

    headers_b = {
        "Authorization": f"Bearer {login_b.json()['access_token']}"
    }

    # User B attempts all operations
    assert client.get(
        f"/tasks/{task_id}", headers=headers_b
    ).status_code == 404

    assert client.put(
        f"/tasks/{task_id}",
        json={
            "title": "Hacked task",
            "description": "Unauthorized update",
            "completed": True
        },
        headers=headers_b
    ).status_code == 404

    assert client.patch(
        f"/tasks/{task_id}",
        json={"title": "Hacked task"},
        headers=headers_b
    ).status_code == 404

    assert client.delete(
        f"/tasks/{task_id}", headers=headers_b
    ).status_code == 404