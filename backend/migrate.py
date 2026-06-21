"""Add columns that didn't exist when the table was first created.

Safe to run multiple times — each ALTER TABLE is wrapped in a try/except so
it silently skips columns that already exist (PostgreSQL raises
DuplicateColumn / code 42701 for that).
"""
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///./dev.db")

from sqlalchemy import text
from backend.database import engine

NEW_WINE_COLUMNS = [
    ("body",        "VARCHAR DEFAULT ''"),
    ("aromatics",   "VARCHAR DEFAULT ''"),
    ("palate",      "VARCHAR DEFAULT ''"),
    ("structure",   "VARCHAR DEFAULT ''"),
    ("finish",      "VARCHAR DEFAULT ''"),
    ("winemaking",  "VARCHAR DEFAULT ''"),
    ("story",       "VARCHAR DEFAULT ''"),
    ("tech_sheet_url", "VARCHAR"),
    ("pronunciation",  "VARCHAR"),
]


def add_column(conn, table: str, column: str, col_type: str):
    # Each ALTER runs in its own transaction so a failure on one column (e.g.
    # "already exists") doesn't abort the rest. In PostgreSQL the first error
    # poisons the whole transaction otherwise.
    try:
        conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {col_type}'))
        conn.commit()
        print(f"  + {table}.{column}")
    except Exception as e:
        conn.rollback()
        msg = str(e).lower()
        if "duplicate" in msg or "already exists" in msg or "42701" in msg:
            print(f"  ~ {table}.{column} (already exists)")
        else:
            print(f"  ! {table}.{column}: {e}", file=sys.stderr)


def main():
    with engine.connect() as conn:
        print("Migrating wine table…")
        for col, ctype in NEW_WINE_COLUMNS:
            add_column(conn, "wine", col, ctype)
    print("Done.")


if __name__ == "__main__":
    # Never let a migration hiccup stop the web server from booting.
    try:
        main()
    except Exception as e:
        print(f"Migration skipped due to error: {e}", file=sys.stderr)
