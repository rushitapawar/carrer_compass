from flask import Blueprint, request, jsonify, session

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import get_db_connection


# ============================================================
# CREATE AUTHENTICATION BLUEPRINT
# ============================================================

auth_bp = Blueprint("auth", __name__)


# ============================================================
# SIGNUP API
# ============================================================

@auth_bp.route("/api/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True) or {}

    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    # Normalize email: trimmed + lowercase (login matches the same way)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")


    # Check required fields

    if not first_name or not last_name or not email or not password:

        return jsonify({
            "success": False,
            "message": "Please fill in all fields"
        }), 400


    # Combine first name and last name

    name = f"{first_name} {last_name}"


    # Hash password

    hashed_password = generate_password_hash(password)


    conn = get_db_connection()


    try:

        # Case-insensitive duplicate check
        existing = conn.execute(
            "SELECT id FROM users WHERE LOWER(email) = ?",
            (email,)
        ).fetchone()

        if existing is not None:

            return jsonify({
                "success": False,
                "message": "Email already exists. Please login instead."
            }), 400

        conn.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        conn.commit()


        return jsonify({
            "success": True,
            "message": "Account created successfully!"
        })


    except Exception as error:

        print("Signup error:", error)


        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 400


    finally:

        conn.close()


# ============================================================
# LOGIN API
# ============================================================
@auth_bp.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    # Normalize email the same way as signup (trimmed + lowercase)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Check required fields
    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        }), 400


    conn = get_db_connection()

    try:

        # Find user by email (case-insensitive so emails stored
        # before normalization still match)
        user = conn.execute(
            """
            SELECT
                id,
                name,
                email,
                password
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,)
        ).fetchone()


        # Email does not exist
        if user is None:

            return jsonify({
                "success": False,
                "message":
                    f"No account found for '{email}'. "
                    "Please sign up first (or check for typos)."
            }), 401


        # Check password
        if not check_password_hash(
            user["password"],
            password
        ):

            return jsonify({
                "success": False,
                "message": "Incorrect password."
            }), 401


        # Create login session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]


        # Check whether profile already exists
        profile = conn.execute(
            """
            SELECT id
            FROM profiles
            WHERE user_id = ?
            """,
            (user["id"],)
        ).fetchone()


        if profile is None:

            next_page = "profile"

        else:

            next_page = "dashboard"


        return jsonify({
            "success": True,
            "message": "Login successful!",
            "name": user["name"],
            "userId": user["id"],
            "nextPage": next_page
        })


    except Exception as error:

        print(
            "Login error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to login. Please try again."
        }), 500


    finally:

        conn.close()

        # =========================================
# SAVE PROFILE
# =========================================

@auth_bp.route("/api/profile", methods=["POST"])
def save_profile():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json() or {}

    full_name = data.get("fullName", "").strip()
    age_group = data.get("ageGroup", "").strip()
    education = data.get("education", "").strip()
    stream = data.get("stream", "").strip()
    interests = data.get("interests", [])
    career_goal = data.get("careerGoal", "").strip()

    if (
        not full_name
        or not age_group
        or not education
        or not stream
        or not interests
        or not career_goal
    ):
        return jsonify({
            "success": False,
            "message": "Please complete all profile information."
        }), 400

    interests_text = ", ".join(interests)

    conn = get_db_connection()

    try:

        conn.execute("""
            INSERT INTO profiles
            (
                user_id,
                full_name,
                age_group,
                education,
                stream,
                interests,
                career_goal
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                full_name = excluded.full_name,
                age_group = excluded.age_group,
                education = excluded.education,
                stream = excluded.stream,
                interests = excluded.interests,
                career_goal = excluded.career_goal
        """, (
            session["user_id"],
            full_name,
            age_group,
            education,
            stream,
            interests_text,
            career_goal
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Profile saved successfully!"
        })

    except Exception as error:

        print("PROFILE ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Unable to save profile."
        }), 500

    finally:
        conn.close()