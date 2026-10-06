from flask import Blueprint, request, jsonify
from database import get_db_connection

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/api/contact", methods=["POST"])
def submit_contact():

    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not subject or not message:
        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        }), 400

    conn = get_db_connection()

    try:

        conn.execute("""
            INSERT INTO contact_messages
            (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            subject,
            message
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Your message has been sent successfully!"
        })

    except Exception as error:

        print("Contact form error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to send your message."
        }), 500

    finally:
        conn.close()