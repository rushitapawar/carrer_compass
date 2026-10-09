"""Favourites APIs: save, list, remove and clear saved careers."""
import sqlite3

from flask import Blueprint, request, session

from auth import login_required
from database import CAREER_SELECT, CAREER_SELECT_C, get_db
from helpers import api_error, api_success, first_present

favourites_bp = Blueprint("favourites", __name__)


def _career_id_from(data):
    """Extract a career ID from a dict (supports query/body key aliases)."""
    raw = first_present(data, "career_id", "careerId", "id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


@favourites_bp.route("/api/saved-careers", methods=["GET"])
@login_required
def saved_careers():
    """List the logged-in user's saved careers (full records)."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                f"""
                SELECT {CAREER_SELECT_C}, s.match_percentage, s.created_at AS saved_at
                FROM saved_careers s
                JOIN careers c ON c.career_id = s.career_id
                WHERE s.user_id = ?
                ORDER BY s.id DESC
                """,
                (session["user_id"],),
            ).fetchall()
    except Exception as error:
        print("Saved careers error:", error)
        return api_error("Unable to load saved careers.", 500)

    careers = [dict(row) for row in rows]
    return api_success(careers=careers, total=len(careers))


@favourites_bp.route("/api/save-career", methods=["POST"])
@login_required
def save_career():
    """Save a career for the user (duplicates are silently ignored)."""
    data = request.get_json(silent=True) or {}
    career_id = _career_id_from(data)
    if career_id is None:
        return api_error("career_id is required.")

    match_percentage = data.get("match_percentage", data.get("matchPercentage"))
    if match_percentage is None:
        match_percentage = None
    else:
        try:
            match_percentage = max(0, min(100, int(match_percentage)))
        except (TypeError, ValueError):
            return api_error("match_percentage must be a number between 0 and 100.")

    try:
        with get_db() as conn:
            career = conn.execute(
                "SELECT career_id FROM careers WHERE career_id = ?",
                (career_id,),
            ).fetchone()
            if career is None:
                return api_error("Career not found.", 404)

            conn.execute(
                """
                INSERT INTO saved_careers (user_id, career_id, match_percentage)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, career_id) DO UPDATE SET
                    match_percentage = COALESCE(
                        excluded.match_percentage, saved_careers.match_percentage
                    )
                """,
                (session["user_id"], career_id, match_percentage),
            )
    except sqlite3.Error as error:
        print("Save career error:", error)
        return api_error("Unable to save the career.", 500)

    return api_success("Career saved successfully!", career_id=career_id)


@favourites_bp.route("/api/remove-career", methods=["DELETE"])
@login_required
def remove_career():
    """Remove one saved career (404 when it was not saved)."""
    data = request.get_json(silent=True) or {}
    career_id = _career_id_from(data)
    if career_id is None:
        career_id = _career_id_from(request.args)
    if career_id is None:
        return api_error("career_id is required.")

    try:
        with get_db() as conn:
            cursor = conn.execute(
                "DELETE FROM saved_careers WHERE user_id = ? AND career_id = ?",
                (session["user_id"], career_id),
            )
            removed = cursor.rowcount
    except sqlite3.Error as error:
        print("Remove career error:", error)
        return api_error("Unable to remove the career.", 500)

    if removed == 0:
        return api_error("Saved career not found.", 404)

    return api_success("Career removed successfully!", career_id=career_id)


@favourites_bp.route("/api/clear-saved-careers", methods=["DELETE"])
@login_required
def clear_saved_careers():
    """Remove every saved career for the logged-in user."""
    try:
        with get_db() as conn:
            cursor = conn.execute(
                "DELETE FROM saved_careers WHERE user_id = ?",
                (session["user_id"],),
            )
            removed = cursor.rowcount
    except sqlite3.Error as error:
        print("Clear saved careers error:", error)
        return api_error("Unable to clear saved careers.", 500)

    return api_success("All saved careers removed.", removed=removed)

