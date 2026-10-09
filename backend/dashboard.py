"""Dashboard API: aggregated statistics for the logged-in user."""
from flask import Blueprint, session

from auth import login_required
from database import get_db
from helpers import api_error, api_success

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard", methods=["GET"])
@login_required
def dashboard():
    """Return user info plus assessment/saved/comparison/catalog statistics."""
    user_id = session["user_id"]

    try:
        with get_db() as conn:
            user = conn.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

            if user is None:
                session.clear()
                return api_error("Please login first.", 401)

            profile = conn.execute(
                "SELECT id FROM profiles WHERE user_id = ?",
                (user_id,),
            ).fetchone()

            assessment_row = conn.execute(
                "SELECT COUNT(*) AS count, MAX(created_at) AS last_at"
                " FROM assessments WHERE user_id = ?",
                (user_id,),
            ).fetchone()

            saved_count = conn.execute(
                "SELECT COUNT(*) FROM saved_careers WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]

            comparison_count = conn.execute(
                "SELECT COUNT(*) FROM comparisons WHERE user_id = ?",
                (user_id,),
            ).fetchone()[0]

            total_careers = conn.execute(
                "SELECT COUNT(*) FROM careers"
            ).fetchone()[0]

            total_sectors = conn.execute(
                "SELECT COUNT(DISTINCT sector) FROM careers"
            ).fetchone()[0]
    except Exception as error:
        print("Dashboard error:", error)
        return api_error("Unable to load the dashboard.", 500)

    assessment_count = assessment_row["count"] or 0

    return api_success(
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
        profile_completed=profile is not None,
        assessment_completed=assessment_count > 0,
        assessment_count=assessment_count,
        last_assessment_at=assessment_row["last_at"],
        saved_career_count=saved_count,
        comparison_count=comparison_count,
        total_careers=total_careers,
        total_sectors=total_sectors,
    )
