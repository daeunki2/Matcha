CREATE TABLE users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    auth_provider VARCHAR(20) NOT NULL DEFAULT 'local',
    provider_user_id VARCHAR(255),

    CONSTRAINT valid_auth_provider
        CHECK (auth_provider IN ('local', 'google', '42')),

    CONSTRAINT valid_auth_credentials
        CHECK (
            (auth_provider = 'local'
                AND password_hash IS NOT NULL
                AND provider_user_id IS NULL)
            OR
            (auth_provider IN ('google', '42')
                AND password_hash IS NULL
                AND provider_user_id IS NOT NULL)
        ),

    CONSTRAINT unique_provider_user
        UNIQUE (auth_provider, provider_user_id)
);

CREATE TABLE email_verification_tokens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ
);

CREATE TABLE password_reset_tokens (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ
);

CREATE TABLE sessions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    refresh_token_hash TEXT UNIQUE
);


CREATE TABLE oauth_pending_signups (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    token_hash TEXT NOT NULL UNIQUE,
    auth_provider VARCHAR(20) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
