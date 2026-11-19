
import pytest
from types import SimpleNamespace
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import db
from app.models.department import Department
from app.routes.employees import validate_employee_data


# --------------------------------------------------
# HELPER FUNCTIONS FOR SIMULATING DATABASE ERRORS
# --------------------------------------------------

def raise_integrity_error(*args, **kwargs):
    raise IntegrityError("INSERT", {}, Exception("Simulated integrity error"))


def raise_sqlalchemy_error(*args, **kwargs):
    raise SQLAlchemyError("Simulated database error")


# --------------------------------------------------
# AUTHENTICATION EDGE CASES
# --------------------------------------------------

def test_register_without_json(client):
    response = client.post(
        "/api/auth/register",
        data="invalid json",
        content_type="application/json"
    )

    assert response.status_code == 400


@pytest.mark.parametrize("payload", [
    {"email": "missing@example.com", "password": "TestPass123"},
    {"name": "Test User", "password": "TestPass123"},
    {"name": "Test User", "email": "missing@example.com"}
])
def test_register_with_missing_fields(client, payload):
    response = client.post(
        "/api/auth/register",
        json=payload
    )

    assert response.status_code == 400


@pytest.mark.parametrize("payload", [
    {
        "name": "   ",
        "email": "emptyname@example.com",
        "password": "TestPass123"
    },
    {
        "name": "Test User",
        "email": "   ",
        "password": "TestPass123"
    }
])
def test_register_with_empty_name_or_email(client, payload):
    response = client.post(
        "/api/auth/register",
        json=payload
    )

    assert response.status_code == 400


def test_register_with_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "short@example.com",
            "password": "123"
        }
    )

    assert response.status_code == 400


def test_login_without_json(client):
    response = client.post(
        "/api/auth/login",
        data="invalid json",
        content_type="application/json"
    )

    assert response.status_code == 400


@pytest.mark.parametrize("payload", [
    {"email": "test@example.com"},
    {"password": "TestPass123"}
])
def test_login_with_missing_fields(client, payload):
    response = client.post(
        "/api/auth/login",
        json=payload
    )

    assert response.status_code == 400


# --------------------------------------------------
# DEPARTMENT EDGE CASES
# --------------------------------------------------

def test_create_department_without_json(client, auth_headers):
    response = client.post(
        "/api/departments/",
        data="invalid json",
        content_type="application/json",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_create_department_with_non_object_json(client, auth_headers):
    response = client.post(
        "/api/departments/",
        json=["Engineering"],
        headers=auth_headers
    )

    assert response.status_code == 400


def test_create_department_with_long_name(client, auth_headers):
    response = client.post(
        "/api/departments/",
        json={"name": "A" * 101},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_create_department_with_integrity_error(
    client, auth_headers, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_integrity_error
    )

    response = client.post(
        "/api/departments/",
        json={"name": "Operations"},
        headers=auth_headers
    )

    assert response.status_code == 409


def test_create_department_with_database_error(
    client, auth_headers, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_sqlalchemy_error
    )

    response = client.post(
        "/api/departments/",
        json={"name": "Operations"},
        headers=auth_headers
    )

    assert response.status_code == 500


def test_get_departments_with_database_error(
    client, auth_headers, monkeypatch
):
    monkeypatch.setattr(
        Department,
        "query",
        SimpleNamespace(all=raise_sqlalchemy_error)
    )

    response = client.get(
        "/api/departments/",
        headers=auth_headers
    )

    assert response.status_code == 500


def test_get_nonexistent_department(client, auth_headers):
    response = client.get(
        "/api/departments/9999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_get_department_with_database_error(
    client, auth_headers, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "get",
        raise_sqlalchemy_error
    )

    response = client.get(
        "/api/departments/1",
        headers=auth_headers
    )

    assert response.status_code == 500


def test_update_nonexistent_department(client, auth_headers):
    response = client.put(
        "/api/departments/9999",
        json={"name": "Updated Department"},
        headers=auth_headers
    )

    assert response.status_code == 404


def test_update_department_without_json(client, auth_headers, department):
    response = client.put(
        f"/api/departments/{department['id']}",
        data="invalid json",
        content_type="application/json",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_department_with_invalid_name_type(
    client, auth_headers, department
):
    response = client.put(
        f"/api/departments/{department['id']}",
        json={"name": 123},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_department_with_integrity_error(
    client, auth_headers, department, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_integrity_error
    )

    response = client.put(
        f"/api/departments/{department['id']}",
        json={"name": "Updated Engineering"},
        headers=auth_headers
    )

    assert response.status_code == 409


def test_update_department_with_database_error(
    client, auth_headers, department, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_sqlalchemy_error
    )

    response = client.put(
        f"/api/departments/{department['id']}",
        json={"name": "Updated Engineering"},
        headers=auth_headers
    )

    assert response.status_code == 500


def test_delete_nonexistent_department(client, auth_headers):
    response = client.delete(
        "/api/departments/9999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_department_with_integrity_error(
    client, auth_headers, department, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_integrity_error
    )

    response = client.delete(
        f"/api/departments/{department['id']}",
        headers=auth_headers
    )

    assert response.status_code == 409


def test_delete_department_with_database_error(
    client, auth_headers, department, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_sqlalchemy_error
    )

    response = client.delete(
        f"/api/departments/{department['id']}",
        headers=auth_headers
    )

    assert response.status_code == 500


# --------------------------------------------------
# EMPLOYEE VALIDATION EDGE CASES
# --------------------------------------------------

@pytest.mark.parametrize("payload", [
    None,
    [],
    "invalid data"
])
def test_employee_validation_with_non_object_data(payload):
    cleaned, error = validate_employee_data(payload)

    assert cleaned is None
    assert error is not None


@pytest.mark.parametrize("payload", [
    {},
    {"name": "Arun", "email": "arun@example.com"},
    {"name": "Arun", "department_id": 1}
])
def test_employee_validation_with_missing_required_fields(payload):
    cleaned, error = validate_employee_data(payload)

    assert cleaned is None
    assert error is not None


@pytest.mark.parametrize("payload", [
    {"name": 123},
    {"name": "   "},
    {"name": "A" * 101},
    {"email": 123},
    {"email": "   "},
    {"email": "invalid-email"},
    {"phone": 123},
    {"phone": "1" * 16},
    {"designation": 123},
    {"designation": "D" * 101},
    {"salary": "35000"},
    {"salary": True},
    {"salary": float("nan")},
    {"salary": -100},
    {"department_id": True},
    {"department_id": 0},
    {"department_id": -1},
    {"department_id": 1.5}
])
def test_employee_validation_with_invalid_fields(payload):
    cleaned, error = validate_employee_data(payload, partial=True)

    assert cleaned is None
    assert error is not None


# --------------------------------------------------
# EMPLOYEE ROUTE EDGE CASES
# --------------------------------------------------

def test_create_employee_without_json(client, auth_headers):
    response = client.post(
        "/api/employees/",
        data="invalid json",
        content_type="application/json",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_get_nonexistent_employee(client, auth_headers):
    response = client.get(
        "/api/employees/9999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_update_nonexistent_employee(client, auth_headers):
    response = client.put(
        "/api/employees/9999",
        json={"designation": "Senior Developer"},
        headers=auth_headers
    )

    assert response.status_code == 404


def test_update_employee_with_empty_body(
    client, auth_headers, department
):
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.update@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    response = client.put(
        f"/api/employees/{employee_id}",
        json={},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_employee_with_invalid_json(
    client, auth_headers, department
):
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.invalid@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    response = client.put(
        f"/api/employees/{employee_id}",
        data="invalid json",
        content_type="application/json",
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_employee_with_invalid_department(
    client, auth_headers, department
):
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.dept@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    response = client.put(
        f"/api/employees/{employee_id}",
        json={"department_id": 9999},
        headers=auth_headers
    )

    assert response.status_code == 404


def test_update_employee_with_duplicate_email(
    client, auth_headers, department
):
    first_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "first@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    second_response = client.post(
        "/api/employees/",
        json={
            "name": "Kumar",
            "email": "second@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = second_response.json["employee"]["id"]

    response = client.put(
        f"/api/employees/{employee_id}",
        json={"email": "first@example.com"},
        headers=auth_headers
    )

    assert response.status_code == 409


def test_create_employee_with_integrity_error(
    client, auth_headers, department, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_integrity_error
    )

    response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.error@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    assert response.status_code == 409


def test_create_employee_with_database_error(
    client, auth_headers, department, monkeypatch
):
    monkeypatch.setattr(
        db.session,
        "commit",
        raise_sqlalchemy_error
    )

    response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.db@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    assert response.status_code == 500


def test_update_employee_with_integrity_error(
    client, auth_headers, department, monkeypatch
):
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.integrity@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    monkeypatch.setattr(
        db.session,
        "commit",
        raise_integrity_error
    )

    response = client.put(
        f"/api/employees/{employee_id}",
        json={"designation": "Senior Developer"},
        headers=auth_headers
    )

    assert response.status_code == 409


def test_update_employee_with_database_error(
    client, auth_headers, department, monkeypatch
):
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.update.db@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    monkeypatch.setattr(
        db.session,
        "commit",
        raise_sqlalchemy_error
    )

    response = client.put(
        f"/api/employees/{employee_id}",
        json={"designation": "Senior Developer"},
        headers=auth_headers
    )

    assert response.status_code == 500


def test_delete_nonexistent_employee(client, auth_headers):
    response = client.delete(
        "/api/employees/9999",
        headers=auth_headers
    )

    assert response.status_code == 404


def test_delete_employee_with_database_error(
    client, auth_headers, department, monkeypatch
):
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Arun",
            "email": "arun.delete.db@example.com",
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    monkeypatch.setattr(
        db.session,
        "commit",
        raise_sqlalchemy_error
    )

    response = client.delete(
        f"/api/employees/{employee_id}",
        headers=auth_headers
    )

    assert response.status_code == 500
