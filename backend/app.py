"""Career Compass Flask application: initializes the database, registers all
API blueprints and serves the existing frontend files (read-only).

Run:
    python carrer_compass/backend/app.py
"""
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, send_from_directory, session

from database import init_db

from auth import auth_bp
from profile import profile_bp
from questionnaire import questionnaire_bp
from careers import careers_bp
from sectors import sectors_bp
from favourites import favourites_bp
from dashboard import dashboard_bp
from contact import contact_bp
from admin import admin_bp

# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

HTML_DIR = PROJECT_DIR / "html"
CSS_DIR = PROJECT_DIR / "css"
JS_DIR = PROJECT_DIR / "js"
IMAGES_DIR = PROJECT_DIR / "images"

# ============================================================
# APPLICATION SETUP
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "career-compass-secret-key")

# Create the database (and import the 500 careers) on startup.
CAREER_COUNT = init_db()
print(f"Career Compass backend ready: {CAREER_COUNT} careers loaded.")

# Register API blueprints.
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(questionnaire_bp)
app.register_blueprint(careers_bp)
app.register_blueprint(sectors_bp)
app.register_blueprint(favourites_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(admin_bp)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health")
def health():
    """Basic liveness check for the backend."""
    return jsonify(success=True, message="Career Compass backend is running.")


@app.errorhandler(404)
def not_found(error):
    """Return JSON errors for API paths, plain text otherwise."""
    from flask import request

    if request.path.startswith("/api/"):
        return jsonify(success=False, message="Endpoint not found."), 404
    return "Page not found.", 404


@app.errorhandler(500)
def server_error(error):
    """Never leak stack traces to API clients."""
    from flask import request

    if request.path.startswith("/api/"):
        return jsonify(success=False, message="Internal server error."), 500
    return "Internal server error.", 500


# ============================================================
# FRONTEND FILES (read-only serving, same as backend_old)
# ============================================================

PROTECTED_PAGES = {
    "dashboard.html",
    "profile.html",
    "questionnaire.html",
    "assessment-intro.html",
    "analyzing.html",
    "results.html",
    "favourites.html",
    "settings.html",
}


@app.route("/")
def home():
    return send_from_directory(HTML_DIR, "index.html")


@app.route("/<page>")
def serve_page(page):
    if page in PROTECTED_PAGES and "user_id" not in session:
        return redirect("/login.html")
    return send_from_directory(HTML_DIR, page)


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(CSS_DIR, filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(JS_DIR, filename)


@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory(IMAGES_DIR, filename)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
