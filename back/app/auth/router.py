from flask import Blueprint, request, jsonify
from psycopg.errors import UniqueViolation

from app.auth import email_service, schemas, service

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

    except email_service.EmailDeliveryError:
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
    except email_service.EmailDeliveryError:
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


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Return the currently authenticated user."""
    access_token = request.cookies.get("access_token")

    if not access_token:
        return jsonify({"message": "Authentication required."}), 401

    payload = service.decode_access_token(access_token)

    if payload is None:
        return jsonify({"message": "Authentication required."}), 401

    user = service.get_authenticated_user(payload)

    if user is None:
        return jsonify({"message": "Authentication required."}), 401

    return jsonify(user), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh_session():
    """Rotate refresh token and issue new authentication cookies."""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return jsonify({
            "message": "Session expired. Please log in again."
        }), 401

    payload = service.decode_refresh_token(refresh_token)

    if payload is None:
        return jsonify({
            "message": "Session expired. Please log in again."
        }), 401

    rotated = service.rotate_refresh_token(refresh_token, payload)

    if rotated is None:
        return jsonify({
            "message": "Session expired. Please log in again."
        }), 401

    access_token = service.create_access_token(
        rotated["user_id"],
        rotated["session_id"],
    )

    response = jsonify({"message": "Session refreshed successfully."})

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
        rotated["refresh_token"],
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/auth",
    )

    return response, 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return jsonify({"message": "Authentication required."}), 401

    payload = service.decode_refresh_token(refresh_token)

    if payload is None:
        return jsonify({"message": "Authentication required."}), 401
    
    session = service.validate_refresh_session(refresh_token, payload)

    if session is None:
        return jsonify({"message": "Authentication required."}), 401
    
    service.revoke_all_sessions(session["user_id"])
    
    response = jsonify({"message": "Logged out successfully."})
    response.delete_cookie("access_token", path="/api")
    response.delete_cookie("refresh_token", path="/api/auth")

    return response, 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "Please check your input."}), 400

    email = data.get("email")

    try:
        schemas.validate_email_format(email)
    except ValueError:
        return jsonify({"message": "Please check your input."}), 400

    try:
        service.request_password_reset(email)
    except email_service.EmailDeliveryError:
        return jsonify({
            "message": "Unable to process your request. Please try again later."
        }), 503

    return jsonify({
        "message": (
            "If an account exists for this email, "
            "you will receive a password reset link."
        )
    }), 202
    
    
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "code": "INVALID_REQUEST",
            "message": "Please send a JSON object.",
        }), 400

    try:
        validated_data = schemas.validate_password_reset(data)
    except ValueError as error:
        code = str(error)

        messages = {
            "INVALID_RESET_TOKEN": "Invalid password reset token.",
            "PASSWORD_REQUIRED": "Please enter a password.",
            "PASSWORD_INVALID": (
                "Password must be at least 8 characters "
                "and must not be common or easily guessed."
            ),
        }

        return jsonify({
            "code": code,
            "message": messages.get(code, "Please check your input."),
        }), 400

    success = service.reset_password(
        validated_data["token"],
        validated_data["password"],
    )

    if not success:
        return jsonify({
            "code": "INVALID_RESET_TOKEN",
            "message": "Invalid or expired password reset link.",
        }), 400

    response = jsonify({
        "message": "Password reset successfully. Please log in again.",
    })

    response.delete_cookie("access_token", path="/api")
    response.delete_cookie("refresh_token", path="/api/auth")

    return response, 200
