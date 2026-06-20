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
    try:
        conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {col_type}'))
        print(f"  + {table}.{column}")
    except Exception as e:
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
        conn.commit()
    print("Done.")


if __name__ == "__main__":
    main()
