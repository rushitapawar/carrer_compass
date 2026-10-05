"""Career Compass Flask app: serves career_interest SQLite data + chatbot API."""
from pathlib import Path
import sqlite3

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "career.db"
TABLE_NAME = "career_interest"

app = Flask(__name__, template_folder=str(BASE_DIR / "templates"))


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html") if (BASE_DIR / "templates" / "index.html").exists() else (
        "Career Compass API is running. Try /careers or /api/careers",
        200,
    )


@app.route("/careers")
def careers():
    search = request.args.get("q", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 50)), 1), 200)
    offset = (page - 1) * per_page

    query = f'SELECT * FROM "{TABLE_NAME}"'
    params: list = []
    if search:
        query += " WHERE title LIKE ? OR element_name LIKE ? OR onet_soc_code LIKE ?"
        like = f"%{search}%"
        params.extend([like, like, like])
    query += " ORDER BY title LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return render_template("careers.html", data=rows, q=search, page=page, per_page=per_page)


@app.route("/api/careers")
def api_careers():
    """JSON API used by frontend JS: /api/careers?q=chief&page=1&per_page=20"""
    search = request.args.get("q", "").strip()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 20)), 1), 200)
    offset = (page - 1) * per_page

    base_filter = ""
    params: list = []
    if search:
        base_filter = " WHERE title LIKE ? OR element_name LIKE ? OR onet_soc_code LIKE ?"
        like = f"%{search}%"
        params = [like, like, like]

    with get_db() as conn:
        total = conn.execute(f'SELECT COUNT(*) FROM "{TABLE_NAME}"{base_filter}', params).fetchone()[0]
        rows = conn.execute(
            f'SELECT * FROM "{TABLE_NAME}"{base_filter} ORDER BY title LIMIT ? OFFSET ?',
            [*params, per_page, offset],
        ).fetchall()

    return jsonify(
        {
            "page": page,
            "per_page": per_page,
            "total": total,
            "results": [dict(r) for r in rows],
        }
    )


# ---------------- Chatbot ----------------
def chatbot_response(message: str) -> str:
    message = message.lower().strip()
    if any(w in message for w in ("hello", "hi", "hey")):
        return "Hello! How can I help you?"
    if "career" in message:
        return "I can help you explore different career options based on your interests and skills."
    if "how are you" in message:
        return "I'm doing great! Thanks for asking."
    if "help" in message:
        return "Sure! You can ask me about careers, interests, skills, or how this website works."
    if "thank" in message:
        return "You're welcome!"
    if "bye" in message:
        return "Goodbye! Have a great day!"
    return "Sorry, I don't understand that yet. Try asking me about careers or interests."


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    return jsonify({"response": chatbot_response(message)})


if __name__ == "__main__":
    if not DB_FILE.exists():
        print(f"WARNING: {DB_FILE} not found. Run 'python database/database.py' first.")
    app.run(debug=True)
