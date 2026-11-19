
def test_user_registration(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully"


def test_duplicate_registration(client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123"
    }

    # Register the user for the first time
    client.post("/api/auth/register", json=user_data)

    # Try registering with the same email
    response = client.post("/api/auth/register", json=user_data)

    assert response.status_code == 409
    assert response.json["error"] == "Email already registered"


def test_user_login(client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123"
    }

    # Register the user
    client.post("/api/auth/register", json=user_data)

    # Login with correct credentials
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json


def test_invalid_login(client):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPass123"
        }
    )

    assert response.status_code == 401
    assert response.json["error"] == "Invalid email or password"


def test_protected_endpoint_without_token(client):
    response = client.get("/api/employees/")

    assert response.status_code == 401

