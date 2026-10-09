"""Career APIs: catalog search, career detail, compare two careers."""
import sqlite3

from flask import Blueprint, request, session

from auth import login_required
from database import CAREER_SELECT, get_db
from helpers import api_error, api_success, first_present

careers_bp = Blueprint("careers", __name__)


@careers_bp.route("/api/career-catalog", methods=["GET"])
def career_catalog():
    """Return careers with optional ?search= and ?sector= filters."""
    search = str(request.args.get("search", "")).strip()
    sector = str(request.args.get("sector", "")).strip()

    params = []
    clauses = []

    if search:
        like = f"%{search}%"
        clauses.append(
            "(career_title LIKE ? OR sector LIKE ? OR short_description LIKE ?"
            " OR important_skills LIKE ? OR common_job_roles LIKE ?)"
        )
        params.extend([like, like, like, like, like])

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
                f"SELECT {CAREER_SELECT} FROM careers{where} ORDER BY career_title",
                params,
            ).fetchall()
    except Exception as error:
        print("Career catalog error:", error)
        return api_error("Unable to load career catalog.", 500)

    careers = [dict(row) for row in rows]
    return api_success(careers=careers, total=total, count=len(careers))


@careers_bp.route("/api/career-detail/<int:career_id>", methods=["GET"])
def career_detail(career_id):
    """Return one complete career record (404 when it does not exist)."""
    try:
        with get_db() as conn:
            row = conn.execute(
                f"SELECT {CAREER_SELECT} FROM careers WHERE career_id = ?",
                (career_id,),
            ).fetchone()
    except Exception as error:
        print("Career detail error:", error)
        return api_error("Unable to load career details.", 500)

    if row is None:
        return api_error("Career not found.", 404)

    return api_success(career=dict(row))


def _extract_career_ids(payload):
    """Read the two career IDs from a dict (supports a few key aliases)."""
    first = first_present(payload, "career_one_id", "careerOneId", "first_id", "first")
    second = first_present(payload, "career_two_id", "careerTwoId", "second_id", "second")
    return first, second


def _load_pair(career_one_id, career_two_id):
    """Fetch both careers; returns (first_dict_or_None, second_dict_or_None)."""
    with get_db() as conn:
        rows = conn.execute(
            f"SELECT {CAREER_SELECT} FROM careers WHERE career_id IN (?, ?)",
            (career_one_id, career_two_id),
        ).fetchall()
    by_id = {row["career_id"]: dict(row) for row in rows}
    return by_id.get(career_one_id), by_id.get(career_two_id)


def _compare_response(career_one_id, career_two_id):
    """Shared logic for GET and POST compare: validate, save, respond."""
    try:
        career_one_id = int(career_one_id)
        career_two_id = int(career_two_id)
    except (TypeError, ValueError):
        return api_error("Both career IDs are required.")

    if career_one_id == career_two_id:
        return api_error("Please select two different careers.")

    try:
        first, second = _load_pair(career_one_id, career_two_id)
    except Exception as error:
        print("Compare load error:", error)
        return api_error("Unable to compare careers.", 500)

    if first is None or second is None:
        return api_error("One or both careers not found.", 404)

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO comparisons (user_id, career_one_id, career_two_id)"
                " VALUES (?, ?, ?)",
                (session["user_id"], career_one_id, career_two_id),
            )
    except sqlite3.Error as error:
        print("Compare save error:", error)
        return api_error("Comparison could not be saved.", 500)

    return api_success(careers=[first, second])


@careers_bp.route("/api/compare-careers", methods=["GET"])
@login_required
def compare_careers_get():
    """Compare using query params (e.g. ?career_one_id=1&career_two_id=2)."""
    career_one_id, career_two_id = _extract_career_ids(request.args)
    return _compare_response(career_one_id, career_two_id)


@careers_bp.route("/api/compare-careers", methods=["POST"])
@login_required
def compare_careers_post():
    """Compare using a JSON body with the two career IDs."""
    data = request.get_json(silent=True) or {}
    career_one_id, career_two_id = _extract_career_ids(data)
    return _compare_response(career_one_id, career_two_id)
