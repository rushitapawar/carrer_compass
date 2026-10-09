"""Authentication APIs: signup, login, logout, session + access decorators."""
import sqlite3
from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db
from helpers import api_error, api_success

auth_bp = Blueprint("auth", __name__)


# ============================================================
# ACCESS DECORATORS
# ============================================================

def login_required(view):
    """Reject requests that have no logged-in user (401)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return api_error("Please login first.", 401)
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    """Reject requests from non-admin or logged-out users (401/403)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is None:
            return api_error("Please login first.", 401)

        try:
            with get_db() as conn:
                row = conn.execute(
                    "SELECT is_admin FROM users WHERE id = ?",
                    (user_id,),
                ).fetchone()
        except Exception as error:
            print("Admin check error:", error)
            return api_error("Unable to verify admin access.", 500)

        if row is None:
            session.clear()
            return api_error("Please login first.", 401)
        if row["is_admin"] != 1:
            return api_error("Admin access required.", 403)

        return view(*args, **kwargs)

    return wrapper


# ============================================================
# SIGNUP
# ============================================================

@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    """Create a new user. Accepts firstName/lastName (frontend) or name."""
    data = request.get_json(silent=True) or {}

    first_name = str(data.get("firstName", "")).strip()
    last_name = str(data.get("lastName", "")).strip()
    name = str(data.get("name", "")).strip() or f"{first_name} {last_name}".strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "") or "")

    if not name or not email or not password:
        return api_error("Please fill in all fields.")
    if "@" not in email or "." not in email.split("@")[-1]:
        return api_error("Please enter a valid email address.")

    try:
        with get_db() as conn:
            existing = conn.execute(
                "SELECT id FROM users WHERE lower(email) = ?",
                (email,),
            ).fetchone()
            if existing is not None:
                return api_error("Email already exists. Please login instead.", 409)

            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
    except sqlite3.IntegrityError:
        return api_error("Email already exists. Please login instead.", 409)
    except Exception as error:
        print("Signup error:", error)
        return api_error("Unable to create account. Please try again.", 500)

    return api_success("Account created successfully!", 201)


# ============================================================
# LOGIN
# ============================================================

@auth_bp.route("/api/login", methods=["POST"])
def login():
    """Verify credentials and store the user in the Flask session."""
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "") or "")

    if not email or not password:
        return api_error("Please fill in all fields.")

    try:
        with get_db() as conn:
            user = conn.execute(
                "SELECT id, name, email, password FROM users WHERE lower(email) = ?",
                (email,),
            ).fetchone()

            if user is None:
                return api_error("Email not found.", 401)
            if not check_password_hash(user["password"], password):
                return api_error("Incorrect password.", 401)

            profile = conn.execute(
                "SELECT id FROM profiles WHERE user_id = ?",
                (user["id"],),
            ).fetchone()
    except Exception as error:
        print("Login error:", error)
        return api_error("Unable to login. Please try again.", 500)

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]

    next_page = "profile" if profile is None else "dashboard"
    return api_success(
        "Login successful!",
        name=user["name"],
        userId=user["id"],
        nextPage=next_page,
    )


# ============================================================
# LOGOUT
# ============================================================

@auth_bp.route("/api/logout", methods=["POST", "GET"])
def logout():
    """Clear the session."""
    session.clear()
    return api_success("Logged out.")


# ============================================================
# SESSION
# ============================================================

@auth_bp.route("/api/session", methods=["GET"])
def current_session():
    """Return the logged-in user (401 when not logged in)."""
    if "user_id" not in session:
        return api_error("Not logged in.", 401)

    try:
        with get_db() as conn:
            user = conn.execute(
                "SELECT id, name, email, is_admin FROM users WHERE id = ?",
                (session["user_id"],),
            ).fetchone()
    except Exception as error:
        print("Session error:", error)
        return api_error("Unable to load session.", 500)

    if user is None:
        session.clear()
        return api_error("Not logged in.", 401)

    return api_success(
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "isAdmin": bool(user["is_admin"]),
        }
    )
