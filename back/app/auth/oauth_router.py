
import re
import psycopg
from flask import Blueprint, request
from app.auth import service

oauth_bp = Blueprint("oauth_complete", __name__)



@oauth_bp.post("/oauth/complete")
def complete_oauth():
    token = request.cookies.get("pending_oauth")

    if not token:
        return {"message": "OAuth signup session not found."}, 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"message": "Invalid request."}, 400

    username = data.get("username")
    if not isinstance(username, str) or not re.fullmatch(
        r"[A-Za-z0-9_]{3,50}", username
    ):
        return {"message": "Invalid username."}, 400

    try:
        user_id = service.complete_pending_oauth_signup(username, token)
    except psycopg.errors.UniqueViolation:
        return {"message": "Username or email already exists."}, 409

    if user_id is None:
        return {"message": "OAuth signup session expired or invalid."}, 401

    response = service.create_login_response(user_id)
    response.delete_cookie("pending_oauth", path="/api/auth")
    return response, 201
