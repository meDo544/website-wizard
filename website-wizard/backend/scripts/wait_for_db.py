import os
import time
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

parsed = urlparse(DATABASE_URL)

while True:
    try:
        conn = psycopg2.connect(
            dbname=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
        )
        conn.close()
        print("✅ Database is ready!")
        break
    except psycopg2.OperationalError:
        print("⏳ Waiting for database...")
        time.sleep(2)