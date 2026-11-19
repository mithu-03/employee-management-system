def test_create_employee(client, auth_headers, department):
    employee_data = {
        "name": "Arun Kumar",
        "email": "arun.test@example.com",
        "phone": "9876543210",
        "designation": "Python Developer",
        "salary": 35000,
        "department_id": department["id"]
    }

    response = client.post(
        "/api/employees/",
        json=employee_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json["employee"]["name"] == "Arun Kumar"
    assert response.json["employee"]["email"] == "arun.test@example.com"

def test_get_all_employees(client, auth_headers, department):
    # First, create an employee
    client.post(
        "/api/employees/",
        json={
            "name": "Arun Kumar",
            "email": "arun.test@example.com",
            "designation": "Python Developer",
            "salary": 35000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    # Fetch all employees
    response = client.get(
        "/api/employees/",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Arun Kumar"
    
def test_get_employee_by_id(client, auth_headers, department):
    # Create an employee
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Priya Sharma",
            "email": "priya.test@example.com",
            "designation": "Backend Developer",
            "salary": 40000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    # Fetch the employee using their ID
    response = client.get(
        f"/api/employees/{employee_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["name"] == "Priya Sharma"
    assert response.json["email"] == "priya.test@example.com"
    
def test_get_employee_by_id(client, auth_headers, department):
    # Create an employee
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Priya Sharma",
            "email": "priya.test@example.com",
            "designation": "Backend Developer",
            "salary": 40000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    # Fetch the employee using their ID
    response = client.get(
        f"/api/employees/{employee_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json["name"] == "Priya Sharma"
    assert response.json["email"] == "priya.test@example.com"
    
def test_update_employee(client, auth_headers, department):
    # Create an employee
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Priya Sharma",
            "email": "priya.update@example.com",
            "designation": "Junior Developer",
            "salary": 30000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    # Update employee details
    update_response = client.put(
        f"/api/employees/{employee_id}",
        json={
            "designation": "Senior Python Developer",
            "salary": 45000
        },
        headers=auth_headers
    )

    assert update_response.status_code == 200
    assert update_response.json["employee"]["designation"] == "Senior Python Developer"
    assert update_response.json["employee"]["salary"] == 45000
    
def test_delete_employee(client, auth_headers, department):
    # Create an employee
    create_response = client.post(
        "/api/employees/",
        json={
            "name": "Rahul Kumar",
            "email": "rahul.delete@example.com",
            "designation": "Software Developer",
            "salary": 40000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    employee_id = create_response.json["employee"]["id"]

    # Delete the employee
    delete_response = client.delete(
        f"/api/employees/{employee_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 200

    # Verify that the employee no longer exists
    get_response = client.get(
        f"/api/employees/{employee_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 404
    
def test_create_employee_with_invalid_email(client, auth_headers, department):
    response = client.post(
        "/api/employees/",
        json={
            "name": "Test Employee",
            "email": "invalid-email",
            "designation": "Developer",
            "salary": 35000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    
def test_create_employee_with_negative_salary(client, auth_headers, department):
    response = client.post(
        "/api/employees/",
        json={
            "name": "Test Employee",
            "email": "salary.test@example.com",
            "designation": "Developer",
            "salary": -5000,
            "department_id": department["id"]
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    
def test_create_employee_with_duplicate_email(client, auth_headers, department):
    employee_data = {
        "name": "Arun Kumar",
        "email": "duplicate@example.com",
        "designation": "Developer",
        "salary": 35000,
        "department_id": department["id"]
    }

    # Create the first employee
    first_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers=auth_headers
    )

    assert first_response.status_code == 201

    # Try creating another employee with the same email
    second_response = client.post(
        "/api/employees/",
        json=employee_data,
        headers=auth_headers
    )

    assert second_response.status_code == 409
    
def test_create_employee_without_token(client, department):
    response = client.post(
        "/api/employees/",
        json={
            "name": "Unauthorized User",
            "email": "unauthorized@example.com",
            "designation": "Developer",
            "salary": 30000,
            "department_id": department["id"]
        }
    )

    assert response.status_code == 401
    
def test_create_employee_with_invalid_department(client, auth_headers):
    response = client.post(
        "/api/employees/",
        json={
            "name": "Test Employee",
            "email": "invalid.dept@example.com",
            "designation": "Developer",
            "salary": 35000,
            "department_id": 9999
        },
        headers=auth_headers
    )

    assert response.status_code == 404