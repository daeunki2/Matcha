from flask import Blueprint, request, jsonify
from psycopg.errors import UniqueViolation

from app.auth import schemas, service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON object"}), 400

    try:
        validated_data = schemas.validate_registration(data)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    try:
        service.register_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
    except UniqueViolation as error:
        constraint = error.diag.constraint_name

        if constraint == "users_username_key":
            return jsonify({
                "error": "Username is already taken."
            }), 409

        if constraint == "users_email_key":
            return jsonify({
                "message": "Request received. Please check your email."
            }), 202

        return jsonify({
            "error": "Unable to process registration."
        }), 500

    except service.EmailDeliveryError:
        return jsonify({
            "error": "Account created, but verification email delivery failed.",
            "code": "EMAIL_DELIVERY_FAILED",
        }), 503

    return jsonify({
        "message": "Request received. Please check your email."
    }), 202


@auth_bp.route("/verify-email", methods=["POST"])
def verify_email_route():
    """Handle an email verification request."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid verification request."}), 400

    token = data.get("token")

    if not isinstance(token, str) or not token:
        return jsonify({"message": "Invalid verification request."}), 400

    if not service.verify_email(token):
        return jsonify({"message": "Invalid or expired verification link."}), 400

    return jsonify({"message": "Your email has been verified successfully."}), 200


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification_route():
    """Handle a verification email resend request."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Please check your input."}), 400

    email = data.get("email")

    try:
        schemas.validate_email_format(email)
    except ValueError:
        return jsonify({"message": "Please check your input."}), 400
    try:
        service.resend_verification_email(email)
    except service.EmailDeliveryError:
        return jsonify({
            "message": "Unable to process your request. Please try again later."
        }),500

    return jsonify({
        "message": "Request received. Please check your email."
    }), 202


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle a login request."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Invalid request."}), 400

    try:
        validated_data = schemas.validate_login(data)
    except ValueError:
        return jsonify({"message": "Please check your input."}), 400

    try:
        user = service.authenticate_user(
            validated_data["email"],
            validated_data["password"],
        )
    except service.EmailNotVerifiedError:
        return jsonify({"message": "Please verify your email."}), 403

    if user is None:
        return jsonify({"message": "Invalid email or password."}), 401

    session_id = service.create_session(user[0])
    access_token = service.create_access_token(user[0], session_id)
    refresh_token = service.create_refresh_token(user[0], session_id)

    response = jsonify({"message": "Login successful."})

    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=15 * 60,
        path="/api",
    )

    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/auth",
    )

    return response, 200