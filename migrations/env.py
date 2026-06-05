from logging.config import fileConfig

import os
import sys

from alembic import context

from sqlalchemy import (
    engine_from_config,
    pool,
)

from dotenv import load_dotenv

# -------------------------------------------------------------------
# ENSURE PROJECT ROOT IS IMPORTABLE
# -------------------------------------------------------------------

BASE_DIR = os.path.abspath(os.getcwd())

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# -------------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------------------------------------------

load_dotenv(override=True)

# -------------------------------------------------------------------
# ALEMBIC CONFIG
# -------------------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------------------
# DATABASE URL
# -------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

print("🚨 ALEMBIC DATABASE_URL:", DATABASE_URL)

if not DATABASE_URL:
    raise RuntimeError(
        "❌ DATABASE_URL is not set"
    )

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL,
)

# -------------------------------------------------------------------
# IMPORT SQLALCHEMY BASE
# -------------------------------------------------------------------

from backend.db.session import Base

# -------------------------------------------------------------------
# IMPORT ALL MODELS
# -------------------------------------------------------------------
#
# IMPORTANT:
# Importing backend.models ensures ALL ORM models are registered
# with SQLAlchemy metadata for Alembic autogenerate.
#
# DO NOT replace this with individual model imports unless required.
#
# This avoids stale imports like:
#
# backend.models.generated_site
#
# after model refactors.
#
# -------------------------------------------------------------------

import backend.models

# -------------------------------------------------------------------
# TARGET METADATA
# -------------------------------------------------------------------

target_metadata = Base.metadata

# -------------------------------------------------------------------
# OFFLINE MIGRATIONS
# -------------------------------------------------------------------

def run_migrations_offline():
    """
    Run migrations in offline mode.
    """

    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# -------------------------------------------------------------------
# ONLINE MIGRATIONS
# -------------------------------------------------------------------

def run_migrations_online():
    """
    Run migrations in online mode.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section
        ),
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

# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()
