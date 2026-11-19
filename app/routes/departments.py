
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app import db
from app.models.department import Department

department_bp = Blueprint("departments", __name__)


# COMMON VALIDATION FUNCTION
def validate_department_name(data):

    if not isinstance(data, dict):
        return None, "Request body must contain a JSON object"

    name = data.get("name")

    if not isinstance(name, str):
        return None, "Department name must be a string"

    name = name.strip()

    if not name:
        return None, "Department name cannot be empty"

    if len(name) > 100:
        return None, "Department name cannot exceed 100 characters"

    return name, None


# CREATE - Add a department
@department_bp.route("/", methods=["POST"])
@jwt_required()
def add_department():

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Valid JSON request body is required"}), 400

    name, error = validate_department_name(data)

    if error:
        return jsonify({"error": error}), 400

    existing = Department.query.filter(
        func.lower(Department.name) == name.lower()
    ).first()

    if existing:
        return jsonify({"error": "Department already exists"}), 409

    department = Department(name=name)

    try:
        db.session.add(department)
        db.session.commit()

        return jsonify({
            "message": "Department created successfully",
            "department": department.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Department already exists"}), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while creating department"}), 500


# READ - Get all departments
@department_bp.route("/", methods=["GET"])
@jwt_required()
def get_departments():

    try:
        departments = Department.query.all()

        return jsonify([
            department.to_dict() for department in departments
        ]), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while retrieving departments"}), 500


# READ - Get department by ID
@department_bp.route("/<int:department_id>", methods=["GET"])
@jwt_required()
def get_department(department_id):

    try:
        department = db.session.get(Department, department_id)

        if not department:
            return jsonify({"error": "Department not found"}), 404

        return jsonify(department.to_dict()), 200

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while retrieving department"}), 500


# UPDATE - Update department
@department_bp.route("/<int:department_id>", methods=["PUT"])
@jwt_required()
def update_department(department_id):

    department = db.session.get(Department, department_id)

    if not department:
        return jsonify({"error": "Department not found"}), 404

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Valid JSON request body is required"}), 400

    name, error = validate_department_name(data)

    if error:
        return jsonify({"error": error}), 400

    existing = Department.query.filter(
        func.lower(Department.name) == name.lower(),
        Department.id != department_id
    ).first()

    if existing:
        return jsonify({"error": "Department name already exists"}), 409

    department.name = name

    try:
        db.session.commit()

        return jsonify({
            "message": "Department updated successfully",
            "department": department.to_dict()
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Department name already exists"}), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while updating department"}), 500


# DELETE - Delete department
@department_bp.route("/<int:department_id>", methods=["DELETE"])
@jwt_required()
def delete_department(department_id):

    department = db.session.get(Department, department_id)

    if not department:
        return jsonify({"error": "Department not found"}), 404

    # Prevent deletion if employees belong to this department
    if department.employees:
        return jsonify({
            "error": "Cannot delete department because employees are assigned to it"
        }), 409

    try:
        db.session.delete(department)
        db.session.commit()

        return jsonify({
            "message": "Department deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "Cannot delete department because employees are assigned to it"
        }), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Database error while deleting department"}), 500
