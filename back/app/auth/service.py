"""Authentication business logic."""
from datetime import datetime, timedelta, timezone
from app.auth.tokens import (create_email_verification_token,hash_email_verification_token,)
from app.db.session import get_connection
from argon2 import PasswordHasher
from app.auth.email_service import EmailDeliveryError, send_verification_email
import logging

logger = logging.getLogger(__name__)

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
    password_hasher = PasswordHasher()
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
