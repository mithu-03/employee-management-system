# Employee Management System – API Documentation

## 1. Project Overview

The Employee Management System is a REST API built using Python and Flask. It provides endpoints to manage employees, departments, and user authentication.

### Technologies Used
- Python
- Flask
- Flask-SQLAlchemy
- MySQL
- Flask-JWT-Extended
- PyMySQL

## 2. Base URL

```text
http://127.0.0.1:5000
```

All endpoints use JSON for request and response data.

## 3. Authentication

The API uses JSON Web Tokens (JWT) to protect employee and department endpoints.

### Register

**Endpoint:** `POST /api/auth/register`

**Authentication:** Not required.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "Password123"
}
```

**Success Response – 201 Created**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

**Possible Error Responses:**
- `400 Bad Request` – Missing or invalid request data, or password shorter than 8 characters.
- `409 Conflict` – Email already registered.

### Login

**Endpoint:** `POST /api/auth/login`

**Authentication:** Not required.

**Request Body:**
```json
{
    "email": "john@example.com",
    "password": "Password123"
}
```

**Success Response – 200 OK**
```json
{
    "message": "Login successful",
    "access_token": "<JWT_ACCESS_TOKEN>",
    "user": {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
}
```

**Possible Error Responses:**
- `400 Bad Request` – Missing or invalid request data.
- `401 Unauthorized` – Invalid email or password.

### Using the Access Token

For all protected endpoints, include the token in the HTTP request header:

```text
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

A valid token is required to access employee and department endpoints.

## 4. Employee Management APIs

All employee endpoints require JWT authentication.

### Create Employee

**Endpoint:** `POST /api/employees/`

**Request Body:**
```json
{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "phone": "9876543210",
    "designation": "Software Engineer",
    "salary": 45000,
    "department_id": 1
}
```

**Success Response – 201 Created**
```json
{
    "message": "Employee created successfully",
    "employee": {
        "id": 1,
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "9876543210",
        "designation": "Software Engineer",
        "salary": 45000,
        "department_id": 1
    }
}
```

**Possible Error Responses:**
- `400 Bad Request` – Invalid or missing employee data.
- `404 Not Found` – Department does not exist.
- `409 Conflict` – Employee email already exists or data conflicts with an existing record.
- `500 Internal Server Error` – Database error.

### Get All Employees

**Endpoint:** `GET /api/employees/`

**Success Response – 200 OK**

Returns a JSON array containing employee records.

### Get Employee by ID

**Endpoint:** `GET /api/employees/<employee_id>`

**Example:** `GET /api/employees/1`

**Success Response – 200 OK**

Returns the employee record matching the supplied ID.

**Possible Error Response:**
- `404 Not Found` – Employee does not exist.

### Update Employee

**Endpoint:** `PUT /api/employees/<employee_id>`

**Example:** `PUT /api/employees/1`

The API supports partial updates. Only the fields that need to be changed should be included.

**Request Body:**
```json
{
    "designation": "Senior Software Engineer",
    "salary": 60000
}
```

**Success Response – 200 OK**
```json
{
    "message": "Employee updated successfully",
    "employee": {
        "id": 1,
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "9876543210",
        "designation": "Senior Software Engineer",
        "salary": 60000,
        "department_id": 1
    }
}
```

**Possible Error Responses:**
- `400 Bad Request` – Invalid or empty request data.
- `404 Not Found` – Employee or specified department does not exist.
- `409 Conflict` – Email already exists or employee data conflicts.
- `500 Internal Server Error` – Database error.

### Delete Employee

**Endpoint:** `DELETE /api/employees/<employee_id>`

**Example:** `DELETE /api/employees/1`

**Success Response – 200 OK**
```json
{
    "message": "Employee deleted successfully"
}
```

**Possible Error Responses:**
- `404 Not Found` – Employee does not exist.
- `500 Internal Server Error` – Database error.

## 5. Department Management APIs

All department endpoints require JWT authentication.

### Create Department

**Endpoint:** `POST /api/departments/`

**Request Body:**
```json
{
    "name": "Engineering"
}
```

**Success Response – 201 Created**
```json
{
    "message": "Department created successfully",
    "department": {
        "id": 1,
        "name": "Engineering"
    }
}
```

**Possible Error Responses:**
- `400 Bad Request` – Invalid department name.
- `409 Conflict` – Department already exists.
- `500 Internal Server Error` – Database error.

### Get All Departments

**Endpoint:** `GET /api/departments/`

**Success Response – 200 OK**

Returns a JSON array containing all department records.

### Get Department by ID

**Endpoint:** `GET /api/departments/<department_id>`

**Example:** `GET /api/departments/1`

**Success Response – 200 OK**

Returns the department matching the supplied ID.

**Possible Error Response:**
- `404 Not Found` – Department does not exist.

### Update Department

**Endpoint:** `PUT /api/departments/<department_id>`

**Example:** `PUT /api/departments/1`

**Request Body:**
```json
{
    "name": "Product Development"
}
```

**Success Response – 200 OK**
```json
{
    "message": "Department updated successfully",
    "department": {
        "id": 1,
        "name": "Product Development"
    }
}
```

**Possible Error Responses:**
- `400 Bad Request` – Invalid department name.
- `404 Not Found` – Department does not exist.
- `409 Conflict` – Department name already exists.
- `500 Internal Server Error` – Database error.

### Delete Department

**Endpoint:** `DELETE /api/departments/<department_id>`

**Example:** `DELETE /api/departments/1`

**Success Response – 200 OK**
```json
{
    "message": "Department deleted successfully"
}
```

**Possible Error Responses:**
- `404 Not Found` – Department does not exist.
- `409 Conflict` – Cannot delete a department while employees are assigned to it.
- `500 Internal Server Error` – Database error.

## 6. HTTP Status Codes

| Status Code | Meaning |
|---|---|
| 200 | OK – Request completed successfully |
| 201 | Created – Resource created successfully |
| 400 | Bad Request – Invalid request data |
| 401 | Unauthorized – Missing or invalid authentication |
| 404 | Not Found – Requested resource does not exist |
| 409 | Conflict – Duplicate or conflicting data |
| 500 | Internal Server Error – Database or server error |

## 7. Validation Rules

### User
- Name and email cannot be empty.
- Email is normalized to lowercase.
- Password must contain at least 8 characters.
- Duplicate email registration is not allowed.

### Employee
- Name must be a non-empty string with a maximum of 100 characters.
- Email must be valid and cannot exceed 120 characters.
- Phone must be a string with a maximum of 15 characters.
- Designation must be a string with a maximum of 100 characters.
- Salary must be a valid, non-negative number.
- Department ID must be a positive integer.
- Employee email must be unique.
- The referenced department must exist.

### Department
- Department name must be a non-empty string.
- Maximum department name length is 100 characters.
- Duplicate names are prevented, including differences in letter case.
- Departments with assigned employees cannot be deleted.

## 8. Running the Application

Activate the virtual environment:

```bash
source venv/bin/activate
```

Start the Flask application:

```bash
python run.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

## 9. Running Automated Tests

Run the test suite:

```bash
python -m pytest -v
```

Run tests with code coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

The project includes automated tests for authentication, employee management, department management, validation, and error handling.