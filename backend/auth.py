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

    data = request.get_json()

    first_name = data.get("firstName", "").strip()
    last_name = data.get("lastName", "").strip()
    email = data.get("email", "").strip()
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

    data = request.get_json()

    email = data.get("email", "").strip()
    password = data.get("password", "")


    # Check required fields

    if not email or not password:

        return jsonify({
            "success": False,
            "message": "Please fill in all fields"
        }), 400


    conn = get_db_connection()


    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()


    conn.close()


    # Check if user exists

    if user is None:

        return jsonify({
            "success": False,
            "message": "Email not found"
        }), 401


    # Check password

    if not check_password_hash(
        user["password"],
        password
    ):

        return jsonify({
            "success": False,
            "message": "Incorrect password"
        }), 401


    # ========================================================
    # SAVE USER IN FLASK SESSION
    # ========================================================

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]


    return jsonify({
        "success": True,
        "message": "Login successful!",
        "name": user["name"]
    })


# ============================================================
# PROFILE API
# ============================================================

@auth_bp.route("/api/profile", methods=["POST"])
def save_profile():

    # Check whether user is logged in

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401


    data = request.get_json()


    # Get profile information

    full_name = data.get(
        "fullName",
        ""
    ).strip()


    age_group = data.get(
        "ageGroup",
        ""
    ).strip()


    education = data.get(
        "education",
        ""
    ).strip()


    stream = data.get(
        "stream",
        ""
    ).strip()


    interests = data.get(
        "interests",
        []
    )


    career_goal = data.get(
        "careerGoal",
        ""
    ).strip()


    # Check required fields

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


    # Convert interests list into text

    interests_text = ", ".join(interests)


    conn = get_db_connection()


    try:

        # Save profile
        # If profile already exists for this user,
        # update it instead.

        conn.execute(
            """
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
            """,
            (
                session["user_id"],
                full_name,
                age_group,
                education,
                stream,
                interests_text,
                career_goal
            )
        )


        conn.commit()


        return jsonify({
            "success": True,
            "message": "Profile saved successfully!"
        })


    except Exception as error:

        print("Profile error:", error)


        return jsonify({
            "success": False,
            "message": "Unable to save profile."
        }), 500


    finally:

        conn.close()