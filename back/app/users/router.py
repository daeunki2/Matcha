from datetime import date
from flask import Blueprint, jsonify, request, g
from app.auth import service as auth_service
from app.auth import email_service
from app.users import service as users_service
from app.auth.decorators import require_auth
import re
from app.auth import schemas
from psycopg.errors import UniqueViolation

users_bp = Blueprint("users", __name__)


@users_bp.route("/users/me/profile", methods=["GET"])
@require_auth
def get_my_profile():
    """Return the authenticated user's profile."""
    profile = users_service.get_my_profile(g.current_user["id"])

    return jsonify({"profile": profile}), 200


@users_bp.route("/users/me/profile", methods=["PATCH"])
@require_auth
def update_my_profile():
    """Validate the authenticated user's profile changes."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"message": "Non-empty JSON object required."}), 400

    allowed_fields = {"gender", "sexual_preference", "bio", "birth_date"}

    if set(data) - allowed_fields:
        return jsonify({"message": "Unknown profile fields."}), 400

    choices = {
        "gender": {"man", "woman", "other"},
        "sexual_preference": {"heterosexual", "homosexual", "bisexual"},
    }

    for field, allowed in choices.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], str) or data[field] not in allowed:
                return jsonify({"message": f"Invalid {field}."}), 400

    if "bio" in data and data["bio"] is not None:
        bio = data["bio"]

        if not isinstance(bio, str):
            return jsonify({"message": "Bio must be a string."}), 400

        bio = bio.strip()

        if len(bio) > 250:
            return jsonify({"message": "Bio must be 250 characters or fewer."}), 400

        data["bio"] = bio or None

    if "birth_date" in data and data["birth_date"] is not None:
        try:
            birth_date = date.fromisoformat(data["birth_date"])
        except (TypeError, ValueError):
            return jsonify({"message": "Invalid birth date."}), 400

        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

        if age < 18:
            return jsonify({"message": "You must be at least 18 years old."}), 400

        data["birth_date"] = birth_date

    profile = users_service.save_my_profile(
        g.current_user["id"],
        data,
    )

    return jsonify({"profile": profile}), 200


@users_bp.route("/users/me", methods=["PATCH"])
@require_auth
def update_user_account():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"message": "Non-empty JSON object required."}), 400
    
    allowed_fields = {"first_name", "last_name"}

    if set(data) - allowed_fields:
        return jsonify({"message": "Unknown account fields."}), 400

    for field in ("first_name", "last_name"):
        if field in data:
            name = data[field]

            if not isinstance(name, str):
                return jsonify({"message": f"Invalid {field}."}), 400

            if not re.fullmatch(r"[a-zA-ZÀ-ÖØ-öø-ÿŒœŠšŽžŸ'-]{1,100}", name):
                return jsonify({"message": f"Invalid {field}."}), 400
    
    user = users_service.update_user_account(
        g.current_user["id"],
        data,
    )

    return jsonify({"user": user}), 200

@users_bp.route("/users/me/email-change", methods=["POST"])
@require_auth
def request_email_change():
    """Request an email address change."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"message": "Non-empty JSON object required."}), 400

    if set(data) != {"new_email", "current_password"}:
        return jsonify({
            "message": "New email and current password are required."
        }), 400

    new_email = data["new_email"]
    current_password = data["current_password"]

    if not isinstance(current_password, str) or not current_password:
        return jsonify({"message": "Invalid password."}), 400

    try:
        schemas.validate_email_format(new_email)
    except ValueError:
        return jsonify({"message": "Invalid email address."}), 400

    try:
        result = users_service.request_email_change(
            g.current_user["id"],
            new_email,
            current_password,
        )
    except email_service.EmailDeliveryError:
        return jsonify({"message": "Email delivery failed."}), 503

    if result == "USER_NOT_FOUND":
        return jsonify({"message": "Authentication required."}), 401

    if result == "EMAIL_CHANGE_NOT_ALLOWED":
        return jsonify({"message": "Email change is not allowed."}), 403

    if result == "INVALID_PASSWORD":
        return jsonify({"message": "Incorrect current password."}), 403

    if result == "SAME_EMAIL":
        return jsonify({"message": "New email must be different."}), 400

    if result == "EMAIL_ALREADY_EXISTS":
        return jsonify({"message": "Email is already in use."}), 409

    if result == "SUCCESS":
        return jsonify({
            "message": "Please verify your new email address."
        }), 202

    return jsonify({"message": "Internal server error."}), 500


@users_bp.route("/users/me/email-change/verify", methods=["POST"])
@require_auth
def verify_email_change():
    """Verify a token and update the user's email address."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"message": "Non-empty JSON object required."}), 400

    if set(data) != {"token"}:
        return jsonify({"message": "Token is required."}), 400

    token = data["token"]

    if not isinstance(token, str) or not token.strip():
        return jsonify({"message": "Invalid token."}), 400

    try:
        result = users_service.verify_email_change(
            g.current_user["id"],
            token,
            g.current_session_id,
        )
    except UniqueViolation as error:
        if error.diag.constraint_name == "users_email_key":
            return jsonify({"message": "Email is already in use."}), 409
        return jsonify({"message": "Internal server error."}), 500

    if result == "USER_NOT_FOUND":
        return jsonify({"message": "Authentication required."}), 401

    if result == "EMAIL_CHANGE_NOT_ALLOWED":
        return jsonify({"message": "Email change is not allowed."}), 403

    if result == "INVALID_TOKEN":
        return jsonify({"message": "Invalid or expired token."}), 400

    if result == "SUCCESS":
        return jsonify({"message": "Email updated successfully."}), 200

    return jsonify({"message": "Internal server error."}), 500