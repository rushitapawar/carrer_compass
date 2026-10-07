import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "userdb.db"
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# USERS TABLE
# ============================================================

def create_users_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# ASSESSMENTS TABLE
# ============================================================

def ensure_column(conn, table, column, definition):
    """Add a column to a table if it does not exist yet.

    SQLite has no "ADD COLUMN IF NOT EXISTS", so the current
    columns are checked first. Safe to run on every start.
    """

    existing_columns = [
        row[1]
        for row in conn.execute(f"PRAGMA table_info({table})")
    ]

    if column not in existing_columns:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def create_assessments_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guide_name TEXT,
            answers TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Additive migration: keep the calculated results
    # next to the raw answers (idempotent).
    ensure_column(conn, "assessments", "scores", "TEXT")
    ensure_column(conn, "assessments", "top_types", "TEXT")
    ensure_column(conn, "assessments", "matches", "TEXT")

    conn.commit()
    conn.close()


# ============================================================
# PROFILES TABLE
# ============================================================

def create_profiles_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            age_group TEXT NOT NULL,
            education TEXT NOT NULL,
            stream TEXT NOT NULL,
            interests TEXT NOT NULL,
            career_goal TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# SAVED CAREERS TABLE
# ============================================================

def create_saved_careers_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            career_title TEXT NOT NULL,
            onet_soc_code TEXT,
            match_percentage INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, career_title),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# CONTACT MESSAGES TABLE
# ============================================================

def create_contact_messages_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()