"""Sector listing API: unique sectors from the careers table."""
from flask import Blueprint

from database import get_db
from helpers import api_error, api_success

sectors_bp = Blueprint("sectors", __name__)


@sectors_bp.route("/api/career-sectors")
def career_sectors():
    """Return all unique sectors present in the careers table (sorted)."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT DISTINCT sector FROM careers ORDER BY sector"
            ).fetchall()
    except Exception as error:
        print("Sectors error:", error)
        return api_error("Unable to load sectors.", 500)

    sectors = [row["sector"] for row in rows]
    return api_success(sectors=sectors, total=len(sectors))
