from flask import Blueprint, jsonify, session
import sqlite3
import os

dashboard = Blueprint("dashboard", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "userdb.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@dashboard.route("/api/dashboard", methods=["GET"])
def get_dashboard():

    # ============================================================
    # ONLY THE LOGGED-IN USER'S DATA IS RETURNED
    # ============================================================

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    conn = get_db()

    try:
        # Get user information
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404

        # Get saved careers
        careers = conn.execute(
            "SELECT id, career_name FROM saved_careers WHERE user_id = ?",
            (user_id,)
        ).fetchall()

        saved_careers = []

        for career in careers:
            saved_careers.append({
                "id": career["id"],
                "name": career["career_name"]
            })

        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            },
            "assessment_completed": False,
            "saved_careers": saved_careers,
            "career_count": len(saved_careers)
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()