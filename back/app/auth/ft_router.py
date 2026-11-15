from flask import Blueprint, url_for, jsonify
from app.auth.ft_oauth import ft
from app.auth import service
from authlib.integrations.base_client.errors import OAuthError
import requests

ft_bp = Blueprint("ft_auth", __name__)


@ft_bp.get("/42")
def ft_login():
    redirect_uri = url_for("ft_auth.ft_callback", _external=True)
    return ft.authorize_redirect(redirect_uri)


@ft_bp.get("/42/callback")
def ft_callback():
    try:
        token = ft.authorize_access_token()
    except OAuthError:
        return {"message": "42 authentication failed or was cancelled."}, 400


    try:
        response = ft.get(
            "https://api.intra.42.fr/v2/me",
            token=token,
            timeout=10,
        )
        response.raise_for_status()
        userinfo = response.json()
    except (requests.RequestException, ValueError):
        return {
            "message": "42 authentication service is temporarily unavailable."
        }, 502


    if not isinstance(userinfo, dict):
        return {"message": "Invalid response from 42."}, 502

    provider_id = userinfo.get("id")
    email = userinfo.get("email")

    if (
        not isinstance(provider_id, int)
        or isinstance(provider_id, bool)
        or not isinstance(email, str)
        or not email
    ):
        return {"message": "Incomplete user information from 42."}, 502

    provider_user_id = str(provider_id)


    user = service.find_oauth_user("42", provider_user_id)

    if user is not None:
        return service.create_login_response(user[0]), 200

    existing_email = service.find_user_by_email(email)

    if existing_email is not None:
        return jsonify({
            "message": "This email is already registered. Please use your original login method."
        }), 409

    pending_token = service.create_pending_oauth_signup(
        provider="42",
        provider_user_id=provider_user_id,
        email=email,
    )

    result = jsonify({"message": "Username required."})
    result.set_cookie(
        "pending_oauth",
        pending_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=600,
        path="/api/auth",
    )

    return result, 200
