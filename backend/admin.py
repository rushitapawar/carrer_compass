"""Admin APIs: manage careers (is_admin = 1 only)."""
import sqlite3

from flask import Blueprint, request

from auth import admin_required
from database import CAREER_COLUMNS, CAREER_SELECT, get_db
from helpers import api_error, api_success, first_present

admin_bp = Blueprint("admin", __name__)

# Columns an admin may create/update (career_id is managed by SQLite).
WRITABLE_COLUMNS = [column for column in CAREER_COLUMNS if column != "career_id"]


def _collect_career_fields(data, require_required=True):
    """Extract career fields from a dict; returns (fields, error_response)."""
    fields = {}
    for column in WRITABLE_COLUMNS:
        if column in data:
            value = data[column]
            if value is None:
                fields[column] = None
            else:
                fields[column] = str(value).strip()

    if require_required:
        problems = []
        if not fields.get("career_title"):
            problems.append("career_title")
        if not fields.get("sector"):
            problems.append("sector")
        if problems:
            return None, api_error(
                "Please provide: " + ", ".join(problems) + ".",
                missing=problems,
            )

    return fields, None


@admin_bp.route("/api/admin/careers", methods=["GET"])
@admin_required
def admin_list_careers():
    """List careers with optional ?search= and ?sector= filters."""
    search = str(request.args.get("search", "")).strip()
    sector = str(request.args.get("sector", "")).strip()

    params = []
    clauses = []
    if search:
        like = f"%{search}%"
        clauses.append("(career_title LIKE ? OR sector LIKE ?)")
        params.extend([like, like])
    if sector:
        clauses.append("sector = ?")
        params.append(sector)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""

    try:
        with get_db() as conn:
            total = conn.execute(
                f"SELECT COUNT(*) FROM careers{where}", params
            ).fetchone()[0]
            rows = conn.execute(
                f"SELECT {CAREER_SELECT} FROM careers{where} ORDER BY career_id",
                params,
            ).fetchall()
    except Exception as error:
        print("Admin list error:", error)
        return api_error("Unable to load careers.", 500)

    careers = [dict(row) for row in rows]
    return api_success(careers=careers, total=total)


@admin_bp.route("/api/admin/careers", methods=["POST"])
@admin_required
def admin_create_career():
    """Create a career (career_title and sector required)."""
    data = request.get_json(silent=True) or {}
    fields, error_response = _collect_career_fields(data)
    if error_response:
        return error_response

    columns = list(fields.keys())
    placeholders = ", ".join("?" for _ in columns)
    sql = (
        f"INSERT INTO careers ({', '.join(columns)}) VALUES ({placeholders})"
    )

    try:
        with get_db() as conn:
            cursor = conn.execute(sql, [fields[column] for column in columns])
            career_id = cursor.lastrowid
            row = conn.execute(
                f"SELECT {CAREER_SELECT} FROM careers WHERE career_id = ?",
                (career_id,),
            ).fetchone()
    except sqlite3.Error as error:
        print("Admin create error:", error)
        return api_error("Unable to create the career.", 500)

    return api_success("Career created successfully!", 201, career=dict(row))


@admin_bp.route("/api/admin/careers/<int:career_id>", methods=["PUT"])
@admin_required
def admin_update_career(career_id):
    """Update the provided fields of one career."""
    data = request.get_json(silent=True) or {}
    fields, error_response = _collect_career_fields(data, require_required=False)
    if error_response:
        return error_response

    if not fields:
        return api_error("No updatable fields provided.")

    # career_title/sector must not be blanked out when provided.
    for required in ("career_title", "sector"):
        if required in fields and not fields[required]:
            return api_error(f"{required} cannot be empty.")

    assignments = ", ".join(f"{column} = ?" for column in fields)
    sql = f"UPDATE careers SET {assignments} WHERE career_id = ?"

    try:
        with get_db() as conn:
            cursor = conn.execute(
                sql, [fields[column] for column in fields] + [career_id]
            )
            if cursor.rowcount == 0:
                return api_error("Career not found.", 404)
            row = conn.execute(
                f"SELECT {CAREER_SELECT} FROM careers WHERE career_id = ?",
                (career_id,),
            ).fetchone()
    except sqlite3.Error as error:
        print("Admin update error:", error)
        return api_error("Unable to update the career.", 500)

    return api_success("Career updated successfully!", career=dict(row))


@admin_bp.route("/api/admin/careers/<int:career_id>", methods=["DELETE"])
@admin_required
def admin_delete_career(career_id):
    """Delete one career (409 when referenced by saved careers/comparisons)."""
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "DELETE FROM careers WHERE career_id = ?",
                (career_id,),
            )
            if cursor.rowcount == 0:
                return api_error("Career not found.", 404)
    except sqlite3.IntegrityError:
        return api_error(
            "Career is referenced by saved careers or comparisons and cannot be deleted.",
            409,
        )
    except sqlite3.Error as error:
        print("Admin delete error:", error)
        return api_error("Unable to delete the career.", 500)

    return api_success("Career deleted successfully!", career_id=career_id)
