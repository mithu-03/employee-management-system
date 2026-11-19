
import pytest

from app import create_app, db


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key-for-flask",
        "JWT_SECRET_KEY": "test-jwt-secret-key-at-least-32-characters-long"
    }

    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Register a test user
    client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )

    # Login and obtain JWT token
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )

    token = response.json["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def department(client, auth_headers):
    response = client.post(
        "/api/departments/",
        json={"name": "Engineering"},
        headers=auth_headers
    )

    return response.json["department"]
