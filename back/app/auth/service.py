import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.auth import tokens
from app.auth.email_service import EmailDeliveryError, send_verification_email
from app.db.session import get_connection

class EmailNotVerifiedError(Exception):
    pass

logger = logging.getLogger(__name__)
password_hasher = PasswordHasher()

def register_user(username, email, password, first_name, last_name):
    """Register a user with a hashed password."""
    password_hash = hash_password(password)
    with get_connection() as conn:
        user_id = create_user(
            conn,
            username,
            email,
            password_hash,
            first_name,
            last_name,
        )
        token = create_verification_record(conn, user_id)
    try:
        send_verification_email(email=email, token=token)
    except EmailDeliveryError:
        logger.exception("Verification email delivery failed")
        raise

    return user_id

def create_user(conn, username, email, password_hash, first_name, last_name):
    """Create a new user in the database."""
    result = conn.execute(
        "INSERT INTO users (username,email,password_hash,first_name,last_name)VALUES (%s, %s, %s, %s, %s)RETURNING id",
        (username, email, password_hash, first_name, last_name),
    )

    user_id = result.fetchone()[0]
    return user_id

def hash_password(password):
    """Hash a plaintext password."""
    return password_hasher.hash(password)


def create_verification_record(conn, user_id):
    """Create and store a one-time email verification token."""
    token = create_email_verification_token()
    token_hash = hash_email_verification_token(token)

    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    conn.execute(
            "INSERT INTO email_verification_tokens (user_id,token_hash,expires_at)VALUES (%s, %s, %s)",
            (user_id, token_hash, expires_at),
        )

    return token


def verify_email(token):
    """Verify a one-time email token and activate the user."""
    token_hash = hash_email_verification_token(token)

    with get_connection() as conn:
        result = conn.execute(
            """
            UPDATE email_verification_tokens
            SET used_at = NOW()
            WHERE token_hash = %s
            AND used_at IS NULL
            AND expires_at > NOW()
            RETURNING user_id
            """,
            (token_hash,),
        )

        row = result.fetchone()

        if row is None:
            return False

        conn.execute(
            """
            UPDATE users
            SET is_verified = TRUE
            WHERE id = %s
            """,
            (row[0],),
        )

    return True

def find_unverified_user(conn, email):
    """Find an unverified user by email."""
    result = conn.execute(
        """
        SELECT id
        FROM users
        WHERE email = %s
        AND is_verified = FALSE
        """,
        (email,),
    )
    row = result.fetchone()
    return row[0] if row is not None else None

def resend_verification_email(email):
    """Resend a verification email to an unverified user."""
    with get_connection() as conn:
        user_id = find_unverified_user(conn, email)

        if user_id is None:
            return

        conn.execute(
            """
            UPDATE email_verification_tokens
            SET expires_at = NOW()
            WHERE user_id = %s
            AND used_at IS NULL
            """,
            (user_id,),
        )

        token = create_verification_record(conn, user_id)

    try:
        send_verification_email(email=email, token=token)
    except EmailDeliveryError:
        logger.exception("Verification email resend failed")
        raise

def authenticate_user(email, password):
    """Find a user by email."""
    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT id, email, password_hash, is_verified
            FROM users
            WHERE email = %s
            """,
            (email,),
        ).fetchone()
    if user is None:
        return None

    if not verify_password(password, user[2]):
        return None

    if not user[3]:
        raise EmailNotVerifiedError()
    return user


def verify_password(password, stored_hash):
    """Verify a password against its stored hash."""
    try:
        return password_hasher.verify(stored_hash, password)
    except VerifyMismatchError:
        return False
    
    

def create_session(user_id):
    """Create a new login session."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    with get_connection() as conn:
        session = conn.execute(
            """
            INSERT INTO sessions (user_id, expires_at)
            VALUES (%s, %s)
            RETURNING id
            """,
            (user_id, expires_at),
        ).fetchone()

    return session[0]

def create_access_token(user_id, session_id):
    """Create a signed access JWT."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }

    secret_key = os.environ["JWT_SECRET_KEY"]

    return jwt.encode(payload, secret_key, algorithm="HS256")

def create_refresh_token(user_id, session_id):
    """Create a signed refresh JWT."""
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),
        "iat": now,
        "exp": now + timedelta(days=7),
    }
    secret_key = os.environ["JWT_SECRET_KEY"]
    refresh_token = jwt.encode(payload, secret_key, algorithm="HS256")
    token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
    
    
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sessions
            SET refresh_token_hash = %s
            WHERE id = %s
            """,
            (token_hash, session_id),
        )
    return refresh_token


def decode_refresh_token(token):
    """Validate and decode a refresh JWT."""
    try:
        payload = jwt.decode(
            token,
            os.environ["JWT_SECRET_KEY"],
            algorithms=["HS256"],
            options={"require": ["sub", "sid", "type", "iat", "exp", "jti"]},
        )
    except jwt.InvalidTokenError:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload

def decode_access_token(token):
    """Validate and decode an access JWT."""
    try:
        payload = jwt.decode(
            token,
            os.environ["JWT_SECRET_KEY"],
            algorithms=["HS256"],
            options={"require": ["sub", "sid", "type", "iat", "exp"]},
        )
    except jwt.InvalidTokenError:
        return None

    if payload.get("type") != "access":
        return None

    return payload

def get_authenticated_user(payload):
    """Return the user associated with a valid session."""
    try:
        user_id = int(payload["sub"])
        session_id = int(payload["sid"])
    except (KeyError, TypeError, ValueError):
        return None

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT
                u.id,
                u.username,
                u.first_name,
                u.last_name,
                u.email,
                u.is_verified
            FROM users AS u
            JOIN sessions AS s ON s.user_id = u.id
            WHERE u.id = %s
            AND s.id = %s
            AND s.revoked_at IS NULL
            AND s.expires_at > NOW()
            """,
            (user_id, session_id),
        ).fetchone()

    if user is None:
        return None

    return {
        "id": user[0],
        "username": user[1],
        "first_name": user[2],
        "last_name": user[3],
        "email": user[4],
        "is_verified": user[5],
    }