from flask import Blueprint, jsonify, session
from database import get_db_connection

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/api/dashboard", methods=["GET"])
def get_dashboard():

    # Check login session
    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    user_id = session["user_id"]

    conn = get_db_connection()


    try:

        # ========================================
        # GET USER INFORMATION
        # ========================================

        user = conn.execute(
            """
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()


        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404


        # ========================================
        # CHECK ASSESSMENT
        # ========================================

        assessment = conn.execute(
            """
            SELECT id
            FROM assessments
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,)
        ).fetchone()


        assessment_completed = (
            assessment is not None
        )


        # ========================================
        # GET SAVED CAREERS
        # ========================================

        careers = conn.execute(
            """
            SELECT
                id,
                career_title,
                onet_soc_code,
                match_percentage,
                created_at
            FROM saved_careers
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        ).fetchall()


        saved_careers = []


        for career in careers:

            saved_careers.append({

                "id":
                    career["id"],

                "name":
                    career["career_title"],

                "onetSocCode":
                    career["onet_soc_code"],

                "matchPercentage":
                    career["match_percentage"],

                "createdAt":
                    career["created_at"]

            })


        # ========================================
        # RETURN DASHBOARD DATA
        # ========================================

        return jsonify({

            "success": True,

            "user": {

                "id":
                    user["id"],

                "name":
                    user["name"],

                "email":
                    user["email"]

            },

            "assessment_completed":
                assessment_completed,

            "saved_careers":
                saved_careers,

            "career_count":
                len(saved_careers)

        })


    except Exception as error:

        print(
            "Dashboard error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load dashboard."

        }), 500


    finally:

        conn.close()