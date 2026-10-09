
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "career_compass.db"

conn = sqlite3.connect(DB_FILE)

try:
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    print("\nDATABASE TABLES:")
    for table in tables:
        print("-", table[0])

    count = conn.execute(
        "SELECT COUNT(*) FROM careers"
    ).fetchone()[0]

    print("\nCAREER COUNT:", count)

    careers = conn.execute("""
        SELECT career_id, career_title, sector
        FROM careers
        ORDER BY career_id
        LIMIT 3
    """).fetchall()

    print("\nFIRST 3 CAREERS:")
    for career in careers:
        print(career)

finally:
    conn.close()
