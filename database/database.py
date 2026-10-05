"""Import 'Career Interest Types.xlsx' into SQLite (career.db).

Run from anywhere:
    python database/database.py
    # or
    python -m database.database  (from project root)
"""
from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "Career Interest Types.xlsx"
DB_FILE = BASE_DIR / "career.db"
TABLE_NAME = "career_interest"


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize Excel headers to safe snake_case SQLite columns."""
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
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"Excel file not found: {EXCEL_FILE}")

    df = pd.read_excel(EXCEL_FILE, sheet_name=0, engine="openpyxl")
    df = clean_columns(df)

    # Basic cleaning: strip strings, drop fully-empty rows
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": None, "None": None, "": None})
    df = df.dropna(how="all")

    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        # Helpful indexes for the app's queries
        conn.execute(f'CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_title ON "{TABLE_NAME}" (title)')
        conn.execute(
            f'CREATE INDEX IF NOT EXISTS idx_{TABLE_NAME}_element ON "{TABLE_NAME}" (element_name)'
        )
        count = conn.execute(f'SELECT COUNT(*) FROM "{TABLE_NAME}"').fetchone()[0]

    print(f"OK: imported {count} rows from '{EXCEL_FILE.name}' -> '{DB_FILE.name}' table '{TABLE_NAME}'")
    print("Columns:", list(df.columns))


if __name__ == "__main__":
    main()
