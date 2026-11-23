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
