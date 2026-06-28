import os

import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()


def build_database_url() -> str:
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

    return database_url


@pytest.fixture
def db_connection():
    connection = psycopg2.connect(build_database_url())

    try:
        yield connection

    finally:
        connection.close()
