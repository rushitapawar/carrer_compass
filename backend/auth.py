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
            "message": "Please fill in all fields."
        }), 400


    conn = get_db_connection()

    try:

        # Find user by email
        user = conn.execute(
            """
            SELECT
                id,
                name,
                email,
                password
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()


        # Email does not exist
        if user is None:

            return jsonify({
                "success": False,
                "message": "Email not found."
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