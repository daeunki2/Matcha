"""Authentication business logic."""

from app.db.session import get_connection
from argon2 import PasswordHasher

def register_user(username, email, password, first_name, last_name):
    """Register a user with a hashed password."""
    password_hash = hash_password(password)

    user_id = create_user(
        username,
        email,
        password_hash,
        first_name,
        last_name,
    )

    return user_id

def create_user(username, email, password_hash, first_name, last_name):
    """Create a new user in the database."""
    with get_connection() as conn:
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
