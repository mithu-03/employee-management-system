def test_create_department(client, auth_headers):
    response = client.post(
        "/api/departments/",
        json={
            "name": "Human Resources"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json["department"]["name"] == "Human Resources"
    
def test_get_all_departments(client, auth_headers):
    # Create a department
    client.post(
        "/api/departments/",
        json={"name": "Human Resources"},
        headers=auth_headers
    )

    # Retrieve all departments
    response = client.get(
        "/api/departments/",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Human Resources"
    
def test_get_department_by_id(client, auth_headers):
    # Create a department
    create_response = client.post(
        "/api/departments/",
        json={"name": "Finance"},
        headers=auth_headers
    )

    department_id = create_response.json["department"]["id"]

    # Retrieve department using its ID
    response = client.get(
        f"/api/departments/{department_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["id"] == department_id
    assert response.json["name"] == "Finance"
    

def test_update_department(client, auth_headers):
    # Create a department
    create_response = client.post(
        "/api/departments/",
        json={"name": "Human Resources"},
        headers=auth_headers
    )

    department_id = create_response.json["department"]["id"]

    # Update department name
    response = client.put(
        f"/api/departments/{department_id}",
        json={"name": "People Operations"},
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["department"]["name"] == "People Operations"


def test_delete_department(client, auth_headers):
    # Create a department
    create_response = client.post(
        "/api/departments/",
        json={"name": "Temporary Department"},
        headers=auth_headers
    )

    department_id = create_response.json["department"]["id"]

    # Delete department
    response = client.delete(
        f"/api/departments/{department_id}",
        headers=auth_headers
    )

    assert response.status_code == 200

    # Confirm department no longer exists
    get_response = client.get(
        f"/api/departments/{department_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 404


def test_delete_department_with_employees(client, auth_headers, department):
    # Create an employee belonging to this department
    client.post(
        "/api/employees/",
        json={
            "name": "Arun Kumar",
            "email": "arun@example.com",
            "phone": "9876543210",
            "designation": "Developer",
            "salary": 35000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    # Attempt to delete department
    response = client.delete(
        f"/api/departments/{department['id']}",
        headers=auth_headers
    )

    assert response.status_code == 409


def test_create_duplicate_department(client, auth_headers):
    # Create first department
    client.post(
        "/api/departments/",
        json={"name": "Finance"},
        headers=auth_headers
    )

    # Try creating the same department again
    response = client.post(
        "/api/departments/",
        json={"name": "Finance"},
        headers=auth_headers
    )

    assert response.status_code == 409


def test_create_department_with_different_case_duplicate(client, auth_headers):
    # Create first department
    client.post(
        "/api/departments/",
        json={"name": "Engineering"},
        headers=auth_headers
    )

    # Try creating the same name with different capitalization
    response = client.post(
        "/api/departments/",
        json={"name": "engineering"},
        headers=auth_headers
    )

    assert response.status_code == 409


def test_create_department_with_empty_name(client, auth_headers):
    response = client.post(
        "/api/departments/",
        json={"name": ""},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_create_department_with_invalid_name_type(client, auth_headers):
    response = client.post(
        "/api/departments/",
        json={"name": 123},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_create_department_without_token(client):
    response = client.post(
        "/api/departments/",
        json={"name": "Engineering"}
    )

    assert response.status_code == 401


def test_update_department_with_empty_name(client, auth_headers):
    # Create a department
    create_response = client.post(
        "/api/departments/",
        json={"name": "Human Resources"},
        headers=auth_headers
    )

    department_id = create_response.json["department"]["id"]

    # Attempt update with an empty name
    response = client.put(
        f"/api/departments/{department_id}",
        json={"name": ""},
        headers=auth_headers
    )

    assert response.status_code == 400


def test_update_department_with_duplicate_name(client, auth_headers):
    # Create two departments
    client.post(
        "/api/departments/",
        json={"name": "Finance"},
        headers=auth_headers
    )

    second_response = client.post(
        "/api/departments/",
        json={"name": "Engineering"},
        headers=auth_headers
    )

    department_id = second_response.json["department"]["id"]

    # Try renaming Engineering to Finance
    response = client.put(
        f"/api/departments/{department_id}",
        json={"name": "Finance"},
        headers=auth_headers
    )

    assert response.status_code == 409
