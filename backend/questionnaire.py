from flask import Blueprint, request, jsonify, session
import json

from database import get_db_connection
from analysis import score_answers


# ============================================================
# CREATE QUESTIONNAIRE BLUEPRINT
# ============================================================

questionnaire_bp = Blueprint(
    "questionnaire",
    __name__
)


# ============================================================
# SAVE ASSESSMENT API
# ============================================================

@questionnaire_bp.route(
    "/api/save-assessment",
    methods=["POST"]
)
def save_assessment():

    # ========================================================
    # CHECK LOGIN
    # ========================================================

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    # ========================================================
    # GET DATA FROM FRONTEND
    # ========================================================

    data = request.get_json(silent=True) or {}

    guide_name = data.get(
        "guideName",
        ""
    ).strip()

    answers = data.get(
        "answers",
        []
    )


    # ========================================================
    # VALIDATE GUIDE
    # ========================================================

    if not guide_name:

        return jsonify({
            "success": False,
            "message": "Please select a career guide."
        }), 400


    # ========================================================
    # VALIDATE ANSWERS
    # ========================================================

    if not answers:

        return jsonify({
            "success": False,
            "message": "No assessment answers received."
        }), 400


    # Your questionnaire contains 25 questions

    if len(answers) != 25:

        return jsonify({
            "success": False,
            "message": "Please complete all 25 questions."
        }), 400


    # ========================================================
    # CALCULATE RIASEC RESULTS
    # (same engine as /api/analyze-assessment)
    # ========================================================

    try:
        scores, top_types = score_answers(answers)

    except ValueError as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


    # ========================================================
    # CONVERT ANSWERS TO JSON TEXT
    # ========================================================

    answers_json = json.dumps(answers)


    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    conn = get_db_connection()


    try:

        # ====================================================
        # SAVE ASSESSMENT FOR LOGGED-IN USER
        # ====================================================

        cursor = conn.execute(
            """
            INSERT INTO assessments
            (
                user_id,
                guide_name,
                answers,
                scores,
                top_types
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                guide_name,
                answers_json,
                json.dumps(scores),
                json.dumps(top_types)
            )
        )


        conn.commit()


        return jsonify({
            "success": True,
            "message": "Assessment saved successfully!",
            "assessmentId": cursor.lastrowid
        })


    except Exception as error:

        print(
            "Assessment error:",
            error
        )


        return jsonify({
            "success": False,
            "message": "Unable to save assessment."
        }), 500


    finally:

        conn.close()