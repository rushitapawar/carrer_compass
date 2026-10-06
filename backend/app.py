from flask import Flask, send_from_directory, session, redirect
import os

from database import (
    create_users_table,
    create_assessments_table,
    create_profiles_table,
    create_saved_careers_table,
    create_contact_messages_table
)

from auth import auth_bp
from questionnaire import questionnaire_bp
from dashboard import dashboard
from chatbot import chatbot_bp
from analysis import analysis_bp
from careers import careers_bp
from favourites import favourites_bp
from contact import contact_bp


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

app = Flask(__name__)

# Secret key for Flask sessions
app.secret_key = "career-compass-secret-key"


# ============================================================
# PROJECT FOLDERS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

HTML_DIR = os.path.join(BASE_DIR, "html")
CSS_DIR = os.path.join(BASE_DIR, "css")
JS_DIR = os.path.join(BASE_DIR, "js")
IMAGES_DIR = os.path.join(BASE_DIR, "images")


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

create_users_table()
create_assessments_table()
create_profiles_table()
create_saved_careers_table()
create_contact_messages_table()



# ============================================================
# REGISTER BLUEPRINTS
# ============================================================

app.register_blueprint(auth_bp)
app.register_blueprint(questionnaire_bp)
app.register_blueprint(dashboard)
app.register_blueprint(chatbot_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(careers_bp)
app.register_blueprint(favourites_bp)
app.register_blueprint(contact_bp)


# ============================================================
# HOMEPAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        HTML_DIR,
        "index.html"
    )


# ============================================================
# PAGES THAT REQUIRE LOGIN
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


# ============================================================
# SERVE HTML PAGES
# ============================================================

@app.route("/<page>")
def serve_page(page):

    # Logged-in pages: redirect to login if no session
    if page in PROTECTED_PAGES and "user_id" not in session:

        return redirect("/login.html")

    return send_from_directory(
        HTML_DIR,
        page
    )


# ============================================================
# SERVE CSS FILES
# ============================================================

@app.route("/css/<path:filename>")
def serve_css(filename):

    return send_from_directory(
        CSS_DIR,
        filename
    )


# ============================================================
# SERVE JAVASCRIPT FILES
# ============================================================

@app.route("/js/<path:filename>")
def serve_js(filename):

    return send_from_directory(
        JS_DIR,
        filename
    )


# ============================================================
# SERVE IMAGE FILES
# ============================================================

@app.route("/images/<path:filename>")
def serve_images(filename):

    return send_from_directory(
        IMAGES_DIR,
        filename
    )


# ============================================================
# RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )