"""Assessment APIs: save an assessment and fetch the latest one."""
import json

from flask import Blueprint, request, session

import analysis
from auth import login_required
from database import get_db
from helpers import api_error, api_success

questionnaire_bp = Blueprint("questionnaire", __name__)


@questionnaire_bp.route("/api/save-assessment", methods=["POST"])
@login_required
def save_assessment():
    """Validate answers, run the analysis and store both as JSON."""
    data = request.get_json(silent=True) or {}
    answers = data.get("answers")

    try:
        result = analysis.analyze(answers)
    except analysis.AnswerError as error:
        return api_error(str(error))
    except Exception as error:
        print("Assessment analysis error:", error)
        return api_error("Unable to analyze the assessment.", 500)

    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO assessments (user_id, answers, result) VALUES (?, ?, ?)",
                (
                    session["user_id"],
                    json.dumps(answers),
                    json.dumps(result, ensure_ascii=False),
                ),
            )
            assessment_id = cursor.lastrowid
    except Exception as error:
        print("Assessment save error:", error)
        return api_error("Unable to save the assessment.", 500)

    return api_success(
        "Assessment saved successfully!",
        201,
        assessmentId=assessment_id,
        riasecScores=result["riasec_scores"],
        topTypes=result["top_types"],
        recommendations=result["recommendations"],
    )


@questionnaire_bp.route("/api/latest-assessment", methods=["GET"])
@login_required
def latest_assessment():
    """Return the user's most recent assessment (assessment: null when none)."""
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT id, answers, result, created_at FROM assessments"
                " WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                (session["user_id"],),
            ).fetchone()
    except Exception as error:
        print("Latest assessment error:", error)
        return api_error("Unable to load the latest assessment.", 500)

    if row is None:
        return api_success(assessment=None)

    try:
        assessment = {
            "id": row["id"],
            "answers": json.loads(row["answers"]),
            "result": json.loads(row["result"]) if row["result"] else None,
            "created_at": row["created_at"],
        }
    except (TypeError, json.JSONDecodeError) as error:
        print("Assessment decode error:", error)
        return api_error("Stored assessment data is corrupted.", 500)

    return api_success(assessment=assessment)
