import secrets
import hashlib


def create_email_verification_token():
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(32)


def hash_email_verification_token(token):
    """Hash an email verification token using SHA-256."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()