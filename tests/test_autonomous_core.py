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
def test_autonomous_core_exists():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    metadata_json->'profile'->'autonomous_core'
                FROM generated_sites
                WHERE generation_status='completed'
                  AND metadata_json IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1;
                """
            )

            row = cursor.fetchone()

        assert row is not None
        assert row[0] is not None

    finally:
        connection.close()


@pytest.mark.integration
def test_autonomous_core_fields():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    metadata_json->'profile'->'autonomous_core'
                FROM generated_sites
                WHERE generation_status='completed'
                  AND metadata_json IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1;
                """
            )

            autonomous_core = cursor.fetchone()[0]

        assert "core_strength" in autonomous_core
        assert "core_entries" in autonomous_core
        assert "core_status" in autonomous_core
        assert "core_source" in autonomous_core
        assert "model_version" in autonomous_core

    finally:
        connection.close()
