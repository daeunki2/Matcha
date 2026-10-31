"""Authentication request validation."""
import hashlib

def validate_registration(data):
    """Validate registration request data."""
    required_fields = (
        "username",
        "email",
        "password",
        "first_name",
        "last_name",
    )

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

        value = data[field]

        if not isinstance(value, str):
            raise ValueError(f"{field} must be a string")

        if not value.strip():
            raise ValueError(f"{field} cannot be empty")
        
        if field == "username" and len(value) > 50:
            raise ValueError(f"{field} is too long")

        if field == "email" and len(value) > 255:
            raise ValueError(f"{field} is too long")

        if field == "last_name" and len(value) > 100:
            raise ValueError(f"{field} is too long")
        if field == "first_name" and len(value) > 100:
            raise ValueError(f"{field} is too long")

    return data




def validate_password(password):
    blocked = {"password", "12345678", "qwerty123"}

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if password.lower() in blocked:
        raise ValueError("Password is too common")


def get_hash_parts(password):