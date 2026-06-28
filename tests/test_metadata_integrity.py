import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

import pytest


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    assert database_url is not None, "DATABASE_URL is not configured."

    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
    )

    database_url = database_url.replace(
        "@postgres:",
        "@localhost:",
    )

    return psycopg2.connect(database_url)


@pytest.mark.integration
def test_metadata_integrity():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM generated_sites
                WHERE generation_status='completed'
                  AND metadata_json IS NOT NULL;
                """
            )

            completed = cursor.fetchone()[0]

        assert completed > 0

    finally:
        connection.close()
