"""Database initialization for the Career Compass backend.

Creates backend/career_compass.db with all application tables and imports the
500 career records from ../database/career_compass_500_careers.csv (the only
source of career data). The import is idempotent: restarting the application
never creates duplicate career rows.

Run standalone:
    python carrer_compass/backend/database.py
    python carrer_compass/backend/database.py --make-admin someone@example.com
"""
import csv
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "career_compass.db"
CSV_FILE = BASE_DIR.parent / "database" / "career_compass_500_careers.csv"

EXPECTED_CAREER_COUNT = 500

# Actual columns of career_compass_500_careers.csv (verified, do not guess).
CAREER_COLUMNS = [
    "career_id",
    "career_title",
    "sector",
    "short_description",
    "important_skills",
    "education_qualification",
    "recommended_courses",
    "salary_range",
    "demand_level",
    "career_roadmap",
    "common_job_roles",
    "career_growth",
    "onet_soc_code",
]

# Explicit column list for SELECT statements.
CAREER_SELECT = ", ".join(CAREER_COLUMNS)

# Same list qualified for JOIN queries (avoids ambiguous-column errors).
CAREER_SELECT_C = ", ".join("c.{0}".format(column) for column in CAREER_COLUMNS)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    full_name TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    education TEXT NOT NULL DEFAULT '',
    bio TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    answers TEXT NOT NULL,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS careers (
    career_id INTEGER PRIMARY KEY AUTOINCREMENT,
    career_title TEXT NOT NULL,
    sector TEXT NOT NULL,
    short_description TEXT NOT NULL DEFAULT '',
    important_skills TEXT NOT NULL DEFAULT '',
    education_qualification TEXT NOT NULL DEFAULT '',
    recommended_courses TEXT NOT NULL DEFAULT '',
    salary_range TEXT NOT NULL DEFAULT '',
    demand_level TEXT NOT NULL DEFAULT '',
    career_roadmap TEXT NOT NULL DEFAULT '',
    common_job_roles TEXT NOT NULL DEFAULT '',
    career_growth TEXT NOT NULL DEFAULT '',
    onet_soc_code TEXT
);

CREATE TABLE IF NOT EXISTS saved_careers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    career_id INTEGER NOT NULL,
    match_percentage INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, career_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (career_id) REFERENCES careers(career_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    career_one_id INTEGER NOT NULL,
    career_two_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (career_one_id) REFERENCES careers(career_id) ON DELETE RESTRICT,
    FOREIGN KEY (career_two_id) REFERENCES careers(career_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_careers_sector ON careers (sector);
CREATE INDEX IF NOT EXISTS idx_careers_title ON careers (career_title);
CREATE INDEX IF NOT EXISTS idx_saved_careers_user ON saved_careers (user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user ON assessments (user_id);
CREATE INDEX IF NOT EXISTS idx_comparisons_user ON comparisons (user_id);
"""


@contextmanager
def get_db():
    """Yield a connection with Row factory and foreign keys enabled.

    Commits on success, rolls back on error, always closes the connection.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _import_careers(conn):
    """Insert all CSV careers with INSERT OR IGNORE (restart-safe, no duplicates)."""
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"Career CSV not found: {CSV_FILE}")

    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        header = [(name or "").strip() for name in (reader.fieldnames or [])]
        if header != CAREER_COLUMNS:
            raise RuntimeError(
                "CSV columns do not match the expected schema.\n"
                f"Expected: {CAREER_COLUMNS}\n"
                f"Got:      {header}"
            )

        rows = []
        for raw in reader:
            rows.append([(raw.get(column) or "").strip() for column in CAREER_COLUMNS])

    if len(rows) != EXPECTED_CAREER_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_CAREER_COUNT} career rows in CSV, found {len(rows)}."
        )

    placeholders = ", ".join("?" for _ in CAREER_COLUMNS)
    sql = (
        f"INSERT OR IGNORE INTO careers ({', '.join(CAREER_COLUMNS)}) "
        f"VALUES ({placeholders})"
    )
    conn.executemany(sql, rows)


def init_db():
    """Create all tables and import the careers. Returns the total career count."""
    with get_db() as conn:
        conn.executescript(SCHEMA)
        _import_careers(conn)
        count = conn.execute("SELECT COUNT(*) FROM careers").fetchone()[0]

    if count < EXPECTED_CAREER_COUNT:
        raise RuntimeError(
            f"Career import incomplete: {count}/{EXPECTED_CAREER_COUNT} rows present."
        )
    return count


def promote_admin(email):
    """Grant admin rights to the user with the given email. Returns True on success."""
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE users SET is_admin = 1 WHERE lower(email) = lower(?)",
            (str(email).strip(),),
        )
        if cursor.rowcount == 0:
            print(f"No user found with email '{email}'.")
            return False
    print(f"User '{email}' is now an admin.")
    return True


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--make-admin":
        sys.exit(0 if promote_admin(sys.argv[2]) else 1)

    try:
        total = init_db()
        print(f"Database ready: {DB_FILE} ({total} careers)")
    except Exception as error:
        print(f"Database initialization failed: {error}", file=sys.stderr)
        sys.exit(1)

