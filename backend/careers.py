from flask import Blueprint, request, jsonify, session
import sqlite3
import os

careers_bp = Blueprint(
    "careers",
    __name__
)

# =========================================================
# CAREER DATABASE PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

CAREER_DB = os.path.join(
    BASE_DIR,
    "database",
    "career.db"
)


# =========================================================
# RIASEC ELEMENT MAPPING
# =========================================================

RIASEC_MAPPING = {
    "Realistic": "R",
    "Investigative": "I",
    "Artistic": "A",
    "Social": "S",
    "Enterprising": "E",
    "Conventional": "C"
}


# =========================================================
# GET CAREER DATA
# =========================================================

def load_career_data():

    conn = sqlite3.connect(CAREER_DB)

    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            onet_soc_code,
            title,
            element_id,
            element_name,
            scale_id,
            scale_name,
            data_value
        FROM career_interest
        """
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# CALCULATE CAREER PROFILES
# =========================================================

def build_career_profiles(rows):

    career_profiles = {}

    for row in rows:

        title = row["title"]
        code = row["onet_soc_code"]
        element_name = row["element_name"]
        data_value = row["data_value"]

        if title is None:
            continue

        if data_value is None:
            continue

        element_name_lower = element_name.lower()

        riasec_type = None

        for name, letter in RIASEC_MAPPING.items():

            if name.lower() in element_name_lower:

                riasec_type = letter
                break

        if riasec_type is None:
            continue

        if title not in career_profiles:

            career_profiles[title] = {
                "title": title,
                "onet_soc_code": code,
                "scores": {
                    "R": 0,
                    "I": 0,
                    "A": 0,
                    "S": 0,
                    "E": 0,
                    "C": 0
                }
            }

        career_profiles[title]["scores"][riasec_type] = float(
            data_value
        )

    return career_profiles


# =========================================================
# CALCULATE MATCH %
# =========================================================

def calculate_match(user_scores, career_scores):

    user_total = sum(user_scores.values())

    career_total = sum(career_scores.values())

    if user_total == 0 or career_total == 0:
        return 0

    # Normalize user scores
    user_normalized = {}

    for key in user_scores:

        user_normalized[key] = (
            user_scores[key] / user_total
        )

    # Normalize career scores
    career_normalized = {}

    for key in career_scores:

        career_normalized[key] = (
            career_scores[key] / career_total
        )

    # Calculate similarity
    difference = 0

    for key in user_normalized:

        difference += abs(
            user_normalized[key]
            -
            career_normalized.get(key, 0)
        )

    # Maximum possible difference = 2
    similarity = 1 - (difference / 2)

    match_percentage = round(
        similarity * 100
    )

    return match_percentage


# =========================================================
# CAREER MATCH API
# =========================================================

@careers_bp.route(
    "/api/career-matches",
    methods=["POST"]
)
def career_matches():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json()

    user_scores = data.get(
        "scores",
        {}
    )

    required_types = [
        "R",
        "I",
        "A",
        "S",
        "E",
        "C"
    ]

    # Validate RIASEC scores
    for riasec_type in required_types:

        if riasec_type not in user_scores:

            return jsonify({
                "success": False,
                "message": "Invalid RIASEC scores."
            }), 400

        try:

            user_scores[riasec_type] = float(
                user_scores[riasec_type]
            )

        except:

            return jsonify({
                "success": False,
                "message": "RIASEC scores must be numbers."
            }), 400

    try:

        rows = load_career_data()

        career_profiles = build_career_profiles(
            rows
        )

        recommendations = []

        for title, career in career_profiles.items():

            match_percentage = calculate_match(
                user_scores,
                career["scores"]
            )

            recommendations.append({

                "title": career["title"],

                "onet_soc_code":
                    career["onet_soc_code"],

                "match":
                    match_percentage,

                "scores":
                    career["scores"]

            })

        # Highest matches first
        recommendations.sort(
            key=lambda career:
                career["match"],
            reverse=True
        )

        # Return top 10 careers
        recommendations = recommendations[:10]

        return jsonify({

            "success": True,

            "matches":
                recommendations

        })

    except Exception as error:

        print(
            "Career matching error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to calculate career matches."

        }), 500

# =========================================================
# CAREER DETAIL API
# =========================================================

@careers_bp.route(
    "/api/career-detail",
    methods=["GET"]
)
def career_detail():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    career_title = request.args.get(
        "title",
        ""
    ).strip()

    if not career_title:

        return jsonify({
            "success": False,
            "message": "Career title is required."
        }), 400

    try:

        rows = load_career_data()

        career_profiles = build_career_profiles(
            rows
        )

        selected_career = None

        for title, career in career_profiles.items():

            if title.lower() == career_title.lower():

                selected_career = career
                break

        if selected_career is None:

            return jsonify({
                "success": False,
                "message": "Career not found."
            }), 404

        return jsonify({

            "success": True,

            "career": {

                "title":
                    selected_career["title"],

                "onetSocCode":
                    selected_career["onet_soc_code"],

                "scores":
                    selected_career["scores"]

            }

        })

    except Exception as error:

        print(
            "Career detail error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load career details."

        }), 500

    # =========================================================
# COMPARE CAREERS API
# =========================================================

@careers_bp.route(
    "/api/compare-careers",
    methods=["GET"]
)
def compare_careers():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    first_title = request.args.get(
        "first",
        ""
    ).strip()

    second_title = request.args.get(
        "second",
        ""
    ).strip()

    if not first_title or not second_title:
        return jsonify({
            "success": False,
            "message": "Two career titles are required."
        }), 400

    if first_title.lower() == second_title.lower():
        return jsonify({
            "success": False,
            "message": "Please select two different careers."
        }), 400

    try:

        rows = load_career_data()

        career_profiles = build_career_profiles(rows)

        first_career = None
        second_career = None

        for title, career in career_profiles.items():

            if title.lower() == first_title.lower():
                first_career = career

            if title.lower() == second_title.lower():
                second_career = career

        if first_career is None:
            return jsonify({
                "success": False,
                "message": "First career not found."
            }), 404

        if second_career is None:
            return jsonify({
                "success": False,
                "message": "Second career not found."
            }), 404

        return jsonify({
            "success": True,
            "careers": [
                {
                    "title": first_career["title"],
                    "onetSocCode": first_career["onet_soc_code"],
                    "scores": first_career["scores"]
                },
                {
                    "title": second_career["title"],
                    "onetSocCode": second_career["onet_soc_code"],
                    "scores": second_career["scores"]
                }
            ]
        })

    except Exception as error:

        print(
            "Compare careers error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to compare careers."
        }), 500
    
# =========================================================
# EXISTING CAREER DATA API
# =========================================================

@careers_bp.route(
    "/api/careers",
    methods=["GET"]
)
def get_careers():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    try:

        rows = load_career_data()

        careers = []

        for row in rows:

            careers.append({

                "onet_soc_code":
                    row["onet_soc_code"],

                "title":
                    row["title"],

                "element_id":
                    row["element_id"],

                "element_name":
                    row["element_name"],

                "scale_id":
                    row["scale_id"],

                "scale_name":
                    row["scale_name"],

                "data_value":
                    row["data_value"]

            })

        return jsonify({

            "success": True,

            "careers":
                careers

        })

    except Exception as error:

        print(
            "Career database error:",
            error
        )

        return jsonify({

            "success": False,

            "message":
                "Unable to load career data."

        }), 500