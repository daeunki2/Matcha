from functools import wraps
from flask import g, jsonify, request
from app.auth import service as auth_service

def require_auth(func):
    """Require a valid access token and an active user session."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.cookies.get("access_token")

        if not access_token:
            return jsonify({"message": "Authentication required."}), 401

        payload = auth_service.decode_access_token(access_token)

        if payload is None:
            return jsonify({"message": "Authentication required."}), 401

        user = auth_service.get_authenticated_user(payload)

        if user is None:
            return jsonify({"message": "Authentication required."}), 401

        g.current_user = user
        g.current_session_id = int(payload["sid"])

        return func(*args, **kwargs)

    return wrapper
