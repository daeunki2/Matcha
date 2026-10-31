from flask import Blueprint, request, jsonify

from app.auth.schemas import validate_registration
from app.auth.service import register_user
from psycopg.errors import UniqueViolation

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON object"}), 400

    try:
        validated_data = validate_registration(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    try:
        user_id = register_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
    except UniqueViolation:
        return jsonify({"error": "Username or email already exists"}), 409

    return jsonify({"user_id": user_id}), 201
