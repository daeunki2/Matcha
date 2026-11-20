"""PostgreSQL database connection utilities."""

import os
from pathlib import Path

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


def initialize_schema():
    """Create the application's tables when the database is empty."""
    schema_path = Path(__file__).with_name("schema.sql")
    schema = schema_path.read_text(encoding="utf-8")

    with get_connection() as conn:
        conn.execute(schema)