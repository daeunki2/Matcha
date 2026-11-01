import os
from email.message import EmailMessage
from urllib.parse import urlencode
import smtplib
import ssl

class EmailDeliveryError(Exception):
    """Raised when an email cannot be delivered."""


def send_verification_email(email, token):
    """Prepare an email verification message."""
    frontend_url = os.environ["FRONTEND_URL"].rstrip("/")
    query = urlencode({"token": token})
    verification_url = f"{frontend_url}/verify-email?{query}"

    message = EmailMessage()
    message["From"] = os.environ["EMAIL_FROM"]
    message["To"] = email
    message["Subject"] = "Verify your Matcha account"

    message.set_content(
        "Welcome to Matcha!\n\n"
        "Click the following link to verify your account:\n"
        f"{verification_url}\n\n"
        "This link expires in one hour."
    )
    try:
        with smtplib.SMTP(
            os.environ["SMTP_HOST"],
            int(os.environ["SMTP_PORT"]),
            timeout=10,
        ) as smtp:
            smtp.starttls(context=ssl.create_default_context())
            smtp.login(
                os.environ["SMTP_USER"],
                os.environ["SMTP_PASSWORD"],
            )
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as error:
        raise EmailDeliveryError("Email sending failed") from error