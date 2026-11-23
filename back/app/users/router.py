from datetime import date
from flask import Blueprint, jsonify, request, g
from app.auth import service as auth_service
from app.users import service as users_service
from app.auth.decorators import require_auth

users_bp = Blueprint("users", __name__)


@users_bp.route("/users/me/profile", methods=["GET"])
def get_my_profile():
    """Return the authenticated user's profile."""
    access_token = request.cookies.get("access_token")

    if not access_token:
        return jsonify({"message": "Authentication required."}), 401

    payload = auth_service.decode_access_token(access_token)

    if payload is None:
        return jsonify({"message": "Authentication required."}), 401

    user = auth_service.get_authenticated_user(payload)

    if user is None:
        return jsonify({"message": "Authentication required."}), 401

    profile = users_service.get_my_profile(user["id"])

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
