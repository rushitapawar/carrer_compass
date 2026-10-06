"""Import career_compass_500_careers.csv into SQLite (career.db).

Creates/updates the `careers` table (500 careers: title, sector, salary,
skills, roadmap, ...). The legacy `career_interest` (RIASEC) table is left
untouched so assessment matching keeps working.

Run from anywhere:
    python database/database.py
    # or
    python -m database.database  (from project root)
"""
from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "career_compass_500_careers.csv"
DB_FILE = BASE_DIR / "career.db"
TABLE_NAME = "careers"


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize CSV headers to safe snake_case SQLite columns."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^0-9a-z]+", "_", regex=True)
        .str.strip("_")
    )
    # o_net_soc_code -> onet_soc_code (easier to query)
    df = df.rename(columns={"o_net_soc_code": "onet_soc_code"})
    return df


def main() -> None:
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    df = clean_columns(df)

    # Basic cleaning: strip strings, drop fully-empty rows
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})
    df = df.dropna(how="all")

    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        # Helpful indexes for the app's queries
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_title ON "{TABLE_NAME}" (career_title)')
        conn.execute(
            f'CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_sector ON "{TABLE_NAME}" (sector)'
        )
        count = conn.execute(f'SELECT COUNT(*) FROM "{TABLE_NAME}"').fetchone()[0]
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]

    print(f"OK: imported {count} rows from '{CSV_FILE.name}' -> '{DB_FILE.name}' table '{TABLE_NAME}'")
    print("Columns:", list(df.columns))
    print("Tables now:", tables)


if __name__ == "__main__":
    main()
