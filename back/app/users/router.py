
from flask import Blueprint, jsonify, request

from app.auth import service as auth_service
from app.users import service as users_service


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
