
from flask import Blueprint, request, jsonify
from psycopg.errors import UniqueViolation

from app.auth.schemas import validate_registration
from app.auth.service import register_user, verify_email
from app.auth.email_service import EmailDeliveryError

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
    except EmailDeliveryError:
        return jsonify({
            "error": "Account created, but verification email delivery failed.",
            "code": "EMAIL_DELIVERY_FAILED",
        }), 503

    return jsonify({"user_id": user_id}), 201


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email_route():
    """Handle an email verification request."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid verification request."}), 400

    token = data.get("token")

    if not isinstance(token, str) or not token:
        return jsonify({"message": "Invalid verification request."}), 400

    if not verify_email(token):
        return jsonify({"message": "Invalid or expired verification link."}), 400

    return jsonify({"message": "Your email has been verified successfully."}), 200
