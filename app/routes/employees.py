
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import math

from app import db
from app.models.employee import Employee
from app.models.department import Department

employee_bp = Blueprint("employees", __name__)


# COMMON VALIDATION FUNCTION
def validate_employee_data(data, partial=False):

    if not isinstance(data, dict):
        return None, "Request body must contain a JSON object"

    required_fields = ["name", "email", "department_id"]

    if not partial:
        for field in required_fields:
            if field not in data or data[field] is None:
                return None, f"{field} is required"

    cleaned = {}

    # Validate name
    if "name" in data:
        name = data["name"]

        if not isinstance(name, str) or not name.strip():
            return None, "Name must be a non-empty string"

        name = name.strip()

        if len(name) > 100:
            return None, "Name cannot exceed 100 characters"

        cleaned["name"] = name

    # Validate email
    if "email" in data:
        email = data["email"]

        if not isinstance(email, str) or not email.strip():
            return None, "Email must be a non-empty string"

        try:
            email = validate_email(
                email.strip(),
                check_deliverability=False
            ).normalized
        except EmailNotValidError:
            return None, "Invalid email format"

        if len(email) > 120:
            return None, "Email cannot exceed 120 characters"

        cleaned["email"] = email

    # Validate phone
    if "phone" in data:
        phone = data["phone"]

        if phone is not None:
            if not isinstance(phone, str):
                return None, "Phone must be a string"

            phone = phone.strip()

            if len(phone) > 15:
                return None, "Phone cannot exceed 15 characters"

        cleaned["phone"] = phone

    # Validate designation
    if "designation" in data:
        designation = data["designation"]

        if designation is not None:
            if not isinstance(designation, str):
                return None, "Designation must be a string"

            designation = designation.strip()

            if len(designation) > 100:
                return None, "Designation cannot exceed 100 characters"

        cleaned["designation"] = designation

    # Validate salary
    if "salary" in data:
        salary = data["salary"]

        if salary is not None:
            if isinstance(salary, bool) or not isinstance(salary, (int, float)):
                return None, "Salary must be a number"

            if not math.isfinite(salary) or salary < 0:
                return None, "Salary must be a valid non-negative number"

            salary = float(salary)

        cleaned["salary"] = salary

    # Validate department ID
    if "department_id" in data:
        department_id = data["department_id"]

        if (
            isinstance(department_id, bool)
            or not isinstance(department_id, int)
            or department_id <= 0
        ):
            return None, "Department ID must be a positive integer"

        cleaned["department_id"] = department_id

    return cleaned, None


# CREATE - Add a new employee
@employee_bp.route("/", methods=["POST"])
@jwt_required()
def add_employee():

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Valid JSON request body is required"}), 400

    cleaned, error = validate_employee_data(data)

    if error:
        return jsonify({"error": error}), 400

    department = db.session.get(
        Department, cleaned["department_id"]
    )

    if not department:
        return jsonify({"error": "Department not found"}), 404

    existing_employee = Employee.query.filter_by(
        email=cleaned["email"]
    ).first()

    if existing_employee:
        return jsonify({"error": "Email already exists"}), 409

    employee = Employee(**cleaned)

    try:
        db.session.add(employee)
        db.session.commit()

        return jsonify({
            "message": "Employee created successfully",
            "employee": employee.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Employee data conflicts with an existing record"}), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while creating employee"}), 500


# READ - Get all employees
@employee_bp.route("/", methods=["GET"])
@jwt_required()
def get_employees():

    employees = Employee.query.all()

    return jsonify([
        employee.to_dict() for employee in employees
    ]), 200


# READ - Get employee by ID
@employee_bp.route("/<int:employee_id>", methods=["GET"])
@jwt_required()
def get_employee(employee_id):

    employee = db.session.get(Employee, employee_id)

    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify(employee.to_dict()), 200


# UPDATE - Update employee details
@employee_bp.route("/<int:employee_id>", methods=["PUT"])
@jwt_required()
def update_employee(employee_id):

    employee = db.session.get(Employee, employee_id)

    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "A non-empty JSON object is required"}), 400

    cleaned, error = validate_employee_data(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    if "department_id" in cleaned:
        department = db.session.get(
            Department, cleaned["department_id"]
        )

        if not department:
            return jsonify({"error": "Department not found"}), 404

    if "email" in cleaned:
        existing_employee = Employee.query.filter(
            Employee.email == cleaned["email"],
            Employee.id != employee_id
        ).first()

        if existing_employee:
            return jsonify({"error": "Email already exists"}), 409

    for field, value in cleaned.items():
        setattr(employee, field, value)

    try:
        db.session.commit()

        return jsonify({
            "message": "Employee updated successfully",
            "employee": employee.to_dict()
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Employee data conflicts with an existing record"}), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while updating employee"}), 500


# DELETE - Delete employee
@employee_bp.route("/<int:employee_id>", methods=["DELETE"])
@jwt_required()
def delete_employee(employee_id):

    employee = db.session.get(Employee, employee_id)

    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    try:
        db.session.delete(employee)
        db.session.commit()

        return jsonify({
            "message": "Employee deleted successfully"
        }), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while deleting employee"}), 500

