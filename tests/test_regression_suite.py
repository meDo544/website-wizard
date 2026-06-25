import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    assert database_url, "DATABASE_URL is not configured."

    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
    )

    database_url = database_url.replace(
        "@postgres:",
        "@localhost:",
    )

    return psycopg2.connect(database_url)


REGRESSION_PROJECTS = [
    "Regression-Test1",
    "Regression-Pizza-Shop",
    "Regression-Law-Firm",
    "Regression-Ecommerce-Store",
]


def test_regression_projects_exist():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for project in REGRESSION_PROJECTS:
                cursor.execute(
                    """
                    SELECT generation_status
                    FROM generated_sites
                    WHERE project_name = %s;
                    """,
                    (project,),
                )

                row = cursor.fetchone()

                assert row is not None, f"{project} not found."
                assert row[0] == "completed"

    finally:
        connection.close()


def test_regression_projects_have_metadata():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            for project in REGRESSION_PROJECTS:
                cursor.execute(
                    """
                    SELECT
                        metadata_json->'profile'->'autonomous_core'
                    FROM generated_sites
                    WHERE project_name = %s;
                    """,
                    (project,),
                )

                row = cursor.fetchone()

                assert row is not None
                assert row[0] is not None

    finally:
        connection.close()
