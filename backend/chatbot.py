from flask import Blueprint, jsonify, request
import os
import sqlite3


# ============================================================
# CHATBOT BLUEPRINT
# ============================================================

chatbot_bp = Blueprint("chatbot", __name__)


# ============================================================
# DATABASE PATH (career.db built from xlsx)
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CAREER_DB = os.path.join(BASE_DIR, "database", "career.db")


# ============================================================
# SMART REPLY: search real careers from career.db
# ============================================================

def search_careers(keyword, limit=5):
    """Search career titles / interests in career.db."""

    if not os.path.exists(CAREER_DB):
        return []

    try:
        conn = sqlite3.connect(CAREER_DB)
        conn.row_factory = sqlite3.Row

        like = f"%{keyword}%"

        try:
            rows = conn.execute(
                """
                SELECT title, element_name, scale_name, data_value
                FROM career_interest
                WHERE title LIKE ? OR element_name LIKE ?
                ORDER BY data_value DESC
                LIMIT ?
                """,
                (like, like, limit),
            ).fetchall()
            result = [dict(r) for r in rows]
            conn.close()
            return result
        except sqlite3.OperationalError:
            conn.close()

        conn = sqlite3.connect(CAREER_DB)
        rows = conn.execute(
            """
            SELECT Title, "Element Name", "Scale Name", "Data Value"
            FROM career_interest
            WHERE Title LIKE ? OR "Element Name" LIKE ?
            LIMIT ?
            """,
            (like, like, limit),
        ).fetchall()
        conn.close()
        return [
            {
                "title": r[0],
                "element_name": r[1],
                "scale_name": r[2],
                "data_value": r[3],
            }
            for r in rows
        ]

    except Exception as error:
        print("Career search error:", error)
        return []


def distinct_values(column, limit=8):
    """Get example values for suggestions."""
    if not os.path.exists(CAREER_DB):
        return []
    try:
        conn = sqlite3.connect(CAREER_DB)
        rows = conn.execute(
            f'SELECT DISTINCT "{column}" FROM career_interest LIMIT ?',
            (limit,),
        ).fetchall()
        conn.close()
        return [r[0] for r in rows if r[0]]
    except Exception:
        return []


# ============================================================
# RULE-BASED BRAIN
# ============================================================

INTEREST_INFO = {
    "realistic": "Realistic people enjoy hands-on, practical work — building, fixing, working outdoors or with tools.",
    "investigative": "Investigative people love thinking, research, science and solving complex problems.",
    "artistic": "Artistic people value creativity, design, music, writing and self-expression.",
    "social": "Social people enjoy helping, teaching, caring for others and teamwork.",
    "enterprising": "Enterprising people like leading, persuading, starting projects and business.",
    "conventional": "Conventional people like order, data, structure and organized work.",
}


def chatbot_response(message):
    text = (message or "").lower().strip()

    if not text:
        return "Please type something so I can help you."

    if any(w in text for w in ("hello", "hi", "hey", "namaste")):
        return (
            "Hello! I am your Career Assistant. "
            "Ask me about careers, interests like Artistic or Investigative, "
            "or type 'help' to see what I can do."
        )

    if "help" in text or "what can you" in text or "option" in text:
        interests = distinct_values("element_name") or distinct_values("Element Name")
        hint = f" Try interests like: {', '.join(interests[:5])}." if interests else ""
        return (
            "Here's what I can do:\n"
            "1. Suggest careers (e.g. 'careers for artistic people')\n"
            "2. Explain interests (e.g. 'what is investigative?')\n"
            "3. Guide you (e.g. 'how it works', 'assessment', 'login')."
            f"{hint}"
        )

    if "how it works" in text or "how does" in text:
        return (
            "How it works: 1) Signup/Login, 2) Complete your Profile, "
            "3) Take the 25-question Assessment, 4) View Results & Dashboard, "
            "5) Save favourites and compare roles."
        )

    if "assessment" in text or "questionnaire" in text or "test" in text:
        return (
            "Go to the Assessment page and answer all 25 questions honestly. "
            "Your answers are saved and used to match careers to your interests."
        )

    if "login" in text or "sign in" in text:
        return "Click Login in the navbar and enter your email + password. New here? Use Signup first."

    if "signup" in text or "sign up" in text or "register" in text:
        return "Click Get Started / Signup, enter your first name, last name, email and password to create an account."

    if "dashboard" in text:
        return "Your Dashboard shows your profile, assessment status and saved careers."

    if "favourite" in text or "favorite" in text or "save" in text:
        return "Open any job role and click Save / Favourite to keep it in your list. View them on the Favourites page."

    if "thank" in text:
        return "You're welcome! Good luck with your career journey."

    if "bye" in text:
        return "Goodbye! Come back anytime for career guidance."

    if "how are you" in text:
        return "I'm doing great! Ready to help you explore careers."

    for key, desc in INTEREST_INFO.items():
        if key in text and any(k in text for k in ("what is", "what are", "mean", "explain")):
            examples = search_careers(key, limit=3)
            if examples:
                titles = ", ".join(sorted({e["title"] for e in examples if e.get("title")})[:3])
                return f"{desc} Example careers: {titles}."
            return desc

    search_keyword = None
    for prefix in ("careers for ", "career for ", "jobs for ", "jobs in ", "suggest ", "show "):
        if prefix in text:
            search_keyword = text.split(prefix, 1)[1].strip(" ?.")
            break

    # Strip filler words: "artistic people" -> "artistic"
    if search_keyword:
        for filler in (" people", " persons", " person", " jobs", " careers", " roles"):
            if search_keyword.endswith(filler):
                search_keyword = search_keyword[: -len(filler)].strip()
        # If multi-word still, try each interest word inside it first
        if " " in search_keyword:
            for key in INTEREST_INFO:
                if key in search_keyword:
                    search_keyword = key
                    break

    if not search_keyword:
        for key in INTEREST_INFO:
            if key in text:
                search_keyword = key
                break

    if not search_keyword and "career" in text:
        examples = distinct_values("title", limit=5)
        if examples:
            return (
                "Tell me an interest (e.g. Artistic, Social, Investigative) "
                "and I'll suggest careers. Some careers in the database: "
                f"{', '.join(examples[:5])}."
            )
        return "Tell me your interest (Artistic, Social, Investigative...) and I'll suggest matching careers."

    if search_keyword:
        results = search_careers(search_keyword, limit=5)
        if results:
            lines = [f"- {r.get('title', '?')} ({r.get('element_name', '')})" for r in results]
            return (
                f"Top careers matching '{search_keyword}':\n"
                + "\n".join(lines)
                + "\nWant more? Try another interest like Social or Enterprising."
            )
        return (
            f"I couldn't find careers for '{search_keyword}'. "
            "Try: Realistic, Investigative, Artistic, Social, Enterprising or Conventional."
        )

    return (
        "Sorry, I don't understand that yet. "
        "Try 'help', 'careers for artistic people', or 'what is investigative?'"
    )


# ============================================================
# API ROUTES
# ============================================================

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    return jsonify({"response": chatbot_response(message)})


@chatbot_bp.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    return jsonify({"response": chatbot_response(message)})


@chatbot_bp.route("/api/chat/health", methods=["GET"])
def chat_health():
    return jsonify({
        "success": True,
        "career_db_found": os.path.exists(CAREER_DB),
        "career_db_path": CAREER_DB,
    })
