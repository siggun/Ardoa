import os
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")

# In production (Railway sets RAILWAY_ENVIRONMENT), refuse to start on the
# SQLite fallback. SQLite lives in the ephemeral container filesystem and is
# wiped on every redeploy, silently losing all data. Fail loud instead.
if os.environ.get("RAILWAY_ENVIRONMENT") and DATABASE_URL.startswith("sqlite"):
    raise RuntimeError(
        "DATABASE_URL is not set in this Railway environment. Add a reference "
        "to the Postgres service: DATABASE_URL = ${{Postgres.DATABASE_URL}}. "
        "Refusing to start on the ephemeral SQLite fallback, which loses data "
        "on every redeploy."
    )

# Railway injects postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
