from app.db.session import get_connection

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