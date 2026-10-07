from flask import Blueprint, request, jsonify, session

from database import get_db_connection


favourites_bp = Blueprint(
    "favourites",
    __name__
)


@favourites_bp.route(
    "/api/save-career",
    methods=["POST"]
)
def save_career():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    career_title = data.get(
        "careerTitle",
        ""
    ).strip()

    onet_soc_code = data.get(
        "onetSocCode",
        ""
    ).strip()

    match_percentage = data.get(
        "matchPercentage",
        0
    )

    if not career_title:
        return jsonify({
            "success": False,
            "message": "Career title is required."
        }), 400

    conn = get_db_connection()

    try:

        conn.execute(
            """
            INSERT INTO saved_careers
            (
                user_id,
                career_title,
                onet_soc_code,
                match_percentage
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(user_id, career_title)
            DO UPDATE SET
                onet_soc_code =
                    excluded.onet_soc_code,
                match_percentage =
                    excluded.match_percentage
            """,
            (
                session["user_id"],
                career_title,
                onet_soc_code,
                match_percentage
            )
        )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Career saved successfully!"
        })

    except Exception as error:

        print(
            "Save career error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to save career."
        }), 500

    finally:
        conn.close()


@favourites_bp.route(
    "/api/saved-careers",
    methods=["GET"]
)
def get_saved_careers():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    conn = get_db_connection()

    try:

        rows = conn.execute(
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
            (session["user_id"],)
        ).fetchall()

        careers = []

        for row in rows:

            careers.append({
                "id": row["id"],
                "careerTitle":
                    row["career_title"],
                "onetSocCode":
                    row["onet_soc_code"],
                "matchPercentage":
                    row["match_percentage"],
                "createdAt":
                    row["created_at"]
            })

        return jsonify({
            "success": True,
            "careers": careers
        })

    except Exception as error:

        print(
            "Get saved careers error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to load saved careers."
        }), 500

    finally:
        conn.close()


@favourites_bp.route(
    "/api/remove-career",
    methods=["POST"]
)
def remove_career():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    career_title = data.get(
        "careerTitle",
        ""
    ).strip()

    if not career_title:
        return jsonify({
            "success": False,
            "message": "Career title is required."
        }), 400

    conn = get_db_connection()

    try:

        conn.execute(
            """
            DELETE FROM saved_careers
            WHERE user_id = ?
            AND career_title = ?
            """,
            (
                session["user_id"],
                career_title
            )
        )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Career removed successfully!"
        })

    except Exception as error:

        print(
            "Remove career error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to remove career."
        }), 500

    finally:
        conn.close()