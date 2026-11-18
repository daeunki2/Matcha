
from flask import Blueprint, url_for, jsonify, redirect
from app.auth.google_oauth import google
from app.auth import service
from authlib.integrations.base_client.errors import OAuthError
import os


google_bp = Blueprint("google_auth", __name__)


@google_bp.get("/google")
def google_login():
    redirect_uri = url_for("google_auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)


@google_bp.get("/google/callback")
def google_callback():
    try:
        token = google.authorize_access_token()
    except OAuthError:
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )

    userinfo = token.get("userinfo")

    if not isinstance(userinfo, dict):
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )

    provider_user_id = userinfo.get("sub")
    email = userinfo.get("email")

    if (
        not isinstance(provider_user_id, str)
        or not provider_user_id
        or not isinstance(email, str)
        or not email
    ):
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )

    if userinfo.get("email_verified") is not True:
        return redirect(
            os.environ["FRONTEND_URL"].rstrip("/")
            + "/login?error=oauth_failed"
        )

    user = service.find_oauth_user("google", provider_user_id)

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
        provider="google",
        provider_user_id=provider_user_id,
        email=email,
    )

    response = jsonify({"message": "Username required."})
    response.set_cookie(
        "pending_oauth",
        pending_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=600,
        path="/api/auth",
    )

    response.status_code = 302
    response.headers["Location"] = (
        os.environ["FRONTEND_URL"].rstrip("/")
        + "/auth/callback?status=username_required"
    )
    return response
