import os
from sqlalchemy import inspect, text
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


# Columns added after the initial schema. SQLModel.create_all() only creates
# missing *tables*, never missing *columns* — so adding a field to a model
# silently breaks queries against an existing table. This map lets us ALTER in
# any columns that are missing on startup, so deploys never go empty again.
WINE_ADDED_COLUMNS = {
    "tech_sheet_url": "VARCHAR",
    "body": "VARCHAR",
    "aromatics": "VARCHAR",
    "palate": "VARCHAR",
    "structure": "VARCHAR",
    "finish": "VARCHAR",
    "winemaking": "VARCHAR",
    "story": "VARCHAR",
}


def ensure_columns():
    """Add any model columns that don't yet exist in the live table."""
    inspector = inspect(engine)
    if "wine" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("wine")}
    with engine.begin() as conn:
        for col, sqltype in WINE_ADDED_COLUMNS.items():
            if col not in existing:
                conn.execute(text(f"ALTER TABLE wine ADD COLUMN {col} {sqltype}"))
        # Backfill the new guest-facing fields from the legacy columns so
        # existing wines aren't blank after the schema change (runs once: only
        # touches rows where the new column is still NULL).
        if "palate" not in existing:
            conn.execute(text(
                "UPDATE wine SET palate = tasting "
                "WHERE palate IS NULL AND tasting IS NOT NULL AND tasting != ''"
            ))
        if "story" not in existing:
            conn.execute(text(
                "UPDATE wine SET story = notes "
                "WHERE story IS NULL AND notes IS NOT NULL AND notes != ''"
            ))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    ensure_columns()


def get_session():
    with Session(engine) as session:
        yield session
