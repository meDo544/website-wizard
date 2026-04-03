from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

import os
import sys

# ---------------------------------------------------
# Ensure app is importable (Docker + local support)
# ---------------------------------------------------
BASE_DIR = os.path.abspath(os.getcwd())
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# ---------------------------------------------------
# Alembic Config
# ---------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------
# Database URL (REQUIRED)
# ---------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL is not set")

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# ---------------------------------------------------
# Import Base + ALL models (CRITICAL)
# ---------------------------------------------------
from backend.core.database import Base

# 🔥 IMPORTANT: Import ALL models here so Alembic detects them
# Add new models to this list as your app grows
import backend.models  # ✅ loads all models via __init__.py

# Optional pattern (recommended for scaling):
# import backend.models  # if __init__.py imports all models

target_metadata = Base.metadata

# ---------------------------------------------------
# Optional: Naming conventions (prevents index issues)
# ---------------------------------------------------
# If not already defined in Base.metadata, consider:
# from sqlalchemy import MetaData
# Base.metadata = MetaData(naming_convention={...})

# ---------------------------------------------------
# Offline migrations
# ---------------------------------------------------
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------
# Online migrations
# ---------------------------------------------------
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------
# Entry point
# ---------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()