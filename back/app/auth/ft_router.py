from flask import Blueprint, url_for, jsonify, redirect
from app.auth.ft_oauth import ft
from app.auth import service
from authlib.integrations.base_client.errors import OAuthError
import requests
import os

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
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )


    try:
        response = ft.get(
            "https://api.intra.42.fr/v2/me",
            token=token,
            timeout=10,
        )
        response.raise_for_status()
        userinfo = response.json()
    except (requests.RequestException, ValueError):
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )


    if not isinstance(userinfo, dict):
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )

    provider_id = userinfo.get("id")
    email = userinfo.get("email")

    if (
        not isinstance(provider_id, int)
        or isinstance(provider_id, bool)
        or not isinstance(email, str)
        or not email
    ):
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )

    provider_user_id = str(provider_id)


    user = service.find_oauth_user("42", provider_user_id)

    if user is not None:
        response = service.create_login_response(user[0])
        response.status_code = 302
        response.headers["Location"] = (
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/auth/callback?status=success"
        )
        return response

    existing_email = service.find_user_by_email(email)

    if existing_email is not None:
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=account_link_required"
        )

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

    result.status_code = 302
    result.headers["Location"] = (
        os.environ["FRONTEND_URL"].rstrip("/")
        + "/auth/callback?status=username_required"
    )
    return result
