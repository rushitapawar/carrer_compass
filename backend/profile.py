"""Profile APIs: GET / PUT (POST alias) /api/profile for logged-in users."""
from flask import Blueprint, request, session

from auth import login_required
from database import get_db
from helpers import api_error, api_success, first_present

profile_bp = Blueprint("profile", __name__)


def _profile_payload(row):
    """Convert a profiles row into the JSON shape returned to clients."""
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "full_name": row["full_name"],
        "phone": row["phone"],
        "location": row["location"],
        "education": row["education"],
        "bio": row["bio"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@profile_bp.route("/api/profile", methods=["GET"])
@login_required
def get_profile():
    """Return the logged-in user's profile (null when not created yet)."""
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?",
                (session["user_id"],),
            ).fetchone()
    except Exception as error:
        print("Profile fetch error:", error)
        return api_error("Unable to load profile.", 500)

    return api_success(profile=_profile_payload(row) if row else None)


@profile_bp.route("/api/profile", methods=["PUT", "POST"])
@login_required
def save_profile():
    """Create or update the profile (POST kept as alias for the existing frontend)."""
    data = request.get_json(silent=True) or {}

    full_name = str(first_present(data, "full_name", "fullName", default="") or "").strip()
    phone = str(first_present(data, "phone", default="") or "").strip()
    location = str(first_present(data, "location", default="") or "").strip()
    education = str(first_present(data, "education", default="") or "").strip()
    bio = str(
        first_present(data, "bio", "careerDescription", "description", default="") or ""
    ).strip()

    if not full_name:
        return api_error("Full name is required.")

    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO profiles (user_id, full_name, phone, location, education, bio)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = excluded.full_name,
                    phone = excluded.phone,
                    location = excluded.location,
                    education = excluded.education,
                    bio = excluded.bio,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (session["user_id"], full_name, phone, location, education, bio),
            )
            row = conn.execute(
                "SELECT * FROM profiles WHERE user_id = ?",
                (session["user_id"],),
            ).fetchone()
    except Exception as error:
        print("Profile save error:", error)
        return api_error("Unable to save profile.", 500)

    return api_success("Profile saved successfully!", profile=_profile_payload(row))
