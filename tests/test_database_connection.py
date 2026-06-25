import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def test_database_connection():
    database_url = os.getenv("DATABASE_URL")

    assert database_url is not None, "DATABASE_URL is not configured."

    # SQLAlchemy → psycopg2
    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
    )

    # Docker hostname → localhost for host-based testing
    database_url = database_url.replace(
        "@postgres:",
        "@localhost:",
    )

    connection = psycopg2.connect(database_url)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()

        assert result[0] == 1

    finally:
        connection.close()
