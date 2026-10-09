"""Contact API: store messages from the contact form."""
import re
import sqlite3

from flask import Blueprint, request, session

from database import get_db
from helpers import api_error, api_success

contact_bp = Blueprint("contact", __name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@contact_bp.route("/api/contact", methods=["POST"])
def contact():
    """Validate and store a contact message (user_id optional)."""
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()

    missing = []
    if not name:
        missing.append("name")
    if not email:
        missing.append("email")
    elif not EMAIL_PATTERN.match(email):
        return api_error("Please provide a valid email address.")
    if not subject:
        missing.append("subject")
    if not message:
        missing.append("message")

    if missing:
        return api_error(
            "Please fill in: " + ", ".join(missing) + ".",
            missing=missing,
        )

    user_id = session.get("user_id")

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO contact_messages (user_id, name, email, subject, message)"
                " VALUES (?, ?, ?, ?, ?)",
                (user_id, name, email, subject, message),
            )
    except sqlite3.Error as error:
        print("Contact error:", error)
        return api_error("Unable to send your message. Please try again.", 500)

    return api_success("Message sent successfully!", 201)
