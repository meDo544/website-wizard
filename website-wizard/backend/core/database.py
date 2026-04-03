from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 🔥 Load DATABASE URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set")

# 🔥 Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # helps avoid stale connections
)

# 🔥 Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 🔥 Base for models
Base = declarative_base()


# =========================================
# 🔥 CRITICAL FIX: IMPORT ALL MODELS HERE
# =========================================
# 👉 This ensures Alembic detects your tables
from backend.models.user import User
# 👉 If you have more models, add them here:
# from backend.audit import Audit


# =========================================
# 🔥 FastAPI DB Dependency
# =========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()