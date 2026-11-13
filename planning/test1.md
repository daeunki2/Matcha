## 1. Frontend Status

**Completed**
- Angular and Docker setup
- Login, signup, and forgot-password pages
- Form validation (email, password, required fields)
- Backend API connection through Angular proxy
- Basic authentication service and token state management

**Remaining**


## 2. Backend Status

**Completed**
- Flask and PostgreSQL setup
- `POST /api/auth/signup` — User registration
- `POST /api/auth/verify-email` — Email verification
- Argon2 password hashing and validation
- Database storage and duplicate checks
- Email verification token generation
- SMTP email delivery

**Remaining**
- Login and logout
- JWT authentication and session management
- Token refresh and revocation
- Password recovery
- Email verification resend
- Automated tests

**Current progress:** Two authentication APIs are implemented. The health-check endpoint (`GET /health`) is also available.

## 3. Required Fixes

| Issue | Action |
|---|---|
| Email verification link not connected | Add verification page |
| Different password validation rules | Align validation policies |
| Email delivery failure recovery | Add resend-verification |
| Errors only shown in console | Display errors in the UI |

## 4. Authentication API Plan

All authentication endpoints will use the `/api/auth` prefix.

| Method | Endpoint | Purpose | Status |
|---|---|---|---|
| POST | `/signup` | Register a new user | Done |
| POST | `/verify-email` | Verify email token | Done |
| POST | `/login` | Authenticate user | Planned |
| POST | `/logout` | Invalidate sessions | Planned |
| GET | `/me` | Get current user | Planned |
| POST | `/refresh` | Refresh authentication tokens | Planned |
| POST | `/resend-verification` | Resend verification email | Planned |
| POST | `/forgot-password` | Request password reset email | Planned |
| POST | `/reset-password` | Set a new password | Planned |

### Proposed Authentication Design

- JWT-based authentication
- Short-lived access tokens
- Refresh tokens for session renewal
- HttpOnly cookies for token storage
- Server-side session tracking
- Logout invalidates all active sessions
- Email verification required for full access

The frontend and backend must agree on request fields, response formats, and error codes before implementation.

## 5. Next Steps

1. Finalize authentication architecture and API contracts.
2. Implement login and password verification.
3. Implement JWT issuance, refresh, and logout.
4. Connect email verification to the frontend.
5. Fix signup responses and post-login navigation.
6. Implement password recovery and email resend.
7. Run authentication integration tests.
8. Start profile management.
9. Implement discovery, likes, and matching.
10. Implement chat and notifications.

**Next priority:** Complete the authentication system before starting profile features.