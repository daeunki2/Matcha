"""PostgreSQL database connection utilities."""

import os

import psycopg


def get_connection():
    """Create and return a PostgreSQL connection."""
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )