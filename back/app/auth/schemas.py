from app.auth.password_security import is_password_acceptable
import re

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

    validate_password(data["password"])
    validate_email_format(data["email"])
    return data


def validate_login(data):
    """Validate login request data."""
    email = data.get("email")
    password = data.get("password")

    validate_email_format(email)

    if not isinstance(password, str) or not password:
        raise ValueError("Invalid password")

    return {
        "email": email,
        "password": password,
    }



def validate_password(password):
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")

    if not is_password_acceptable(password):
        raise ValueError("Password is too weak")
    
def validate_email_format(email):
    """Validate basic email address format."""
    if not isinstance(email, str):
        raise ValueError("Invalid email format")

    if len(email) > 255:
        raise ValueError("Email is too long")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Invalid email format")



