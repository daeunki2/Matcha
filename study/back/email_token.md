## Email Verification — Technical Decision

### Requirement
Matcha requires users to receive an email containing a unique account verification link after registration.

### Options Considered

| Solution | Description |
|---|---|
| Resend API | Sends emails through an external HTTP API. |
| Gmail SMTP | Sends emails using Gmail's SMTP server. |
| Mailpit | Captures emails locally for development and testing. |

### Selected Solution: Gmail SMTP

chose **Gmail SMTP** because:
- It supports sending real verification emails.
- Python provides a built-in SMTP library (`smtplib`).
- No custom domain or external email API is required.
- The same implementation can be reused for password reset emails.

### Implementation Overview

1. Flask creates a user and generates a unique verification token.
2. PostgreSQL stores the token hash and expiration time.
3. Flask sends a verification link using Gmail SMTP.
4. The user clicks the link.
5. Flask validates the token and marks the account as verified.

**Status:** Token generation and database structure are implemented. Gmail SMTP integration and token verification are pending.