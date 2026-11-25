from app.db.session import get_connection
from datetime import datetime, timedelta, timezone
from app.auth import tokens, email_service
from app.auth import service as auth_service

def is_profile_completed(user_id):
    """Check whether a user profile exists."""
    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM user_profiles
                WHERE user_id = %s
            )
            """,
            (user_id,),
        ).fetchone()

    return result[0]

def get_permissions(profile_completed):
    """Return permissions based on profile completion status."""
    return {
        "can_edit_profile": True,
        "can_browse_profiles": profile_completed,
        "can_like": profile_completed,
        "can_chat": profile_completed,
    }
    
def get_my_profile(user_id):
    """Return user profile information."""
    with get_connection() as conn:
        user_profile = conn.execute(
            """
            SELECT
                user_id,
                gender,
                sexual_preference,
                bio,
                birth_date
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,),
        ).fetchone()

    if user_profile is None:
        return None

    return {
        "user_id": user_profile[0],
        "gender": user_profile[1],
        "sexual_preference": user_profile[2],
        "bio": user_profile[3],
        "birth_date": (
            user_profile[4].isoformat()
            if user_profile[4] is not None
            else None
        ),
    }
    


def save_my_profile(user_id, data):
    """Create or partially update a user's profile."""
    fields = ("gender", "sexual_preference", "bio", "birth_date")

    columns = [field for field in fields if field in data]

    insert_columns = ["user_id", *columns]
    insert_values = [user_id, *(data[field] for field in columns)]

    column_names = ", ".join(insert_columns)
    placeholders = ", ".join(["%s"] * len(insert_columns))

    updates = ", ".join(
        f"{field} = EXCLUDED.{field}"
        for field in columns
    )

    query = f"""
        INSERT INTO user_profiles ({column_names})
        VALUES ({placeholders})
        ON CONFLICT (user_id)
        DO UPDATE SET
            {updates},
            updated_at = NOW()
    """

    with get_connection() as conn:
        conn.execute(query, insert_values)

    return get_my_profile(user_id)


def update_user_account(user_id, data):
    fields = ("first_name", "last_name")

    columns = [field for field in fields if field in data]
    values = [data[field] for field in columns]

    updates = ", ".join(
        f"{field} = %s" for field in columns
    )

    query = f"""
        UPDATE users
        SET {updates}
        WHERE id = %s
        RETURNING id, username, first_name, last_name
    """

    with get_connection() as conn:
        user = conn.execute(
            query,
            [*values, user_id],
        ).fetchone()

    return {
        "id": user[0],
        "username": user[1],
        "first_name": user[2],
        "last_name": user[3],
    }
    

def request_email_change(user_id, new_email, current_password):
    """Request verification of a new email address."""
    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT email, auth_provider, password_hash
            FROM users
            WHERE id = %s
            FOR UPDATE
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return "USER_NOT_FOUND"

        if user[1] != "local":
            return "EMAIL_CHANGE_NOT_ALLOWED"

        if not auth_service.verify_password(current_password, user[2]):
            return "INVALID_PASSWORD"

        if user[0] == new_email:
            return "SAME_EMAIL"

        existing_user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            AND id != %s
            """,
            (new_email, user_id),
        ).fetchone()

        if existing_user is not None:
            return "EMAIL_ALREADY_EXISTS"

        conn.execute(
            """
            UPDATE email_change_tokens
            SET expires_at = NOW()
            WHERE user_id = %s
            AND used_at IS NULL
            AND expires_at > NOW()
            """,
            (user_id,),
        )

        token = tokens.create_random_token()
        token_hash = tokens.hash_token(token)

        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        conn.execute(
            """
            INSERT INTO email_change_tokens
                (user_id, new_email, token_hash, expires_at)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, new_email, token_hash, expires_at),
        )

    email_service.send_email_change_email(new_email, token)

    return "SUCCESS"

def verify_email_change(user_id, token, current_session_id):
    """Verify an email change token and revoke other sessions."""
    token_hash = tokens.hash_token(token)

    with get_connection() as conn:
        user = conn.execute(
            """
            SELECT email, auth_provider
            FROM users
            WHERE id = %s
            FOR UPDATE
            """,
            (user_id,),
        ).fetchone()

        if user is None:
            return "USER_NOT_FOUND"

        if user[1] != "local":
            return "EMAIL_CHANGE_NOT_ALLOWED"

        session = conn.execute(
            """
            SELECT id
            FROM sessions
            WHERE id = %s
            AND user_id = %s
            AND revoked_at IS NULL
            AND expires_at > NOW()
            FOR UPDATE
            """,
            (current_session_id, user_id),
        ).fetchone()

        if session is None:
            return "USER_NOT_FOUND"

        result = conn.execute(
            """
            UPDATE email_change_tokens
            SET used_at = NOW()
            WHERE token_hash = %s
            AND user_id = %s
            AND used_at IS NULL
            AND expires_at > NOW()
            RETURNING new_email
            """,
            (token_hash, user_id),
        ).fetchone()

        if result is None:
            return "INVALID_TOKEN"

        new_email = result[0]

        conn.execute(
            """
            UPDATE users
            SET email = %s
            WHERE id = %s
            """,
            (new_email, user_id),
        )

        conn.execute(
            """
            UPDATE password_reset_tokens
            SET expires_at = NOW()
            WHERE user_id = %s
            AND used_at IS NULL
            AND expires_at > NOW()
            """,
            (user_id,),
        )

        conn.execute(
            """
            UPDATE sessions
            SET revoked_at = NOW()
            WHERE user_id = %s
            AND id != %s
            AND revoked_at IS NULL
            """,
            (user_id, current_session_id),
        )

    return "SUCCESS"