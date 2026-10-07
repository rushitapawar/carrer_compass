from flask import Blueprint, request, jsonify, session
import sqlite3
import json
import os
from difflib import get_close_matches, SequenceMatcher

from database import get_db_connection

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
# TITLE MATCHING HELPERS
#
# The 500-career catalog (careers table) and the RIASEC
# dataset (career_interest table) use different titles and
# most catalog rows have no usable O*NET code, so catalog
# careers are matched to RIASEC profiles by normalized
# title with a fuzzy fallback (stdlib difflib only).
# =========================================================

# Cache: normalized catalog title -> career_interest title.
# career.db does not change while the app is running.

_RESOLVED_TITLE_CACHE = {}

# Token table produced by build_interest_title_index()
_TOKEN_INDEX = {"index": None, "entries": []}


def normalize_title(title):
    """Lowercase a title and strip punctuation/parentheses."""

    if not title:
        return ""

    title = str(title).lower()

    # Remove parenthetical notes: "Actors (stage)" -> "Actors"
    if "(" in title:
        title = title.split("(", 1)[0]

    cleaned = []

    for char in title:
        if char.isalnum() or char.isspace():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return " ".join("".join(cleaned).split()).strip()


def singular_form(title):
    """Naive singular form so plural titles still match."""

    words = title.split()

    if not words:
        return title

    last = words[-1]

    if last.endswith("ies") and len(last) > 4:
        words[-1] = last[:-3] + "y"
    elif last.endswith("es") and len(last) > 3:
        words[-1] = last[:-2]
    elif last.endswith("s") and len(last) > 2:
        words[-1] = last[:-1]

    return " ".join(words)


def build_interest_title_index(titles):
    """Index normalized/singular titles -> original title.

    Also prepares a token table (all original titles split into
    words) used by resolve_interest_title for subset matching.
    """

    index = {}

    for title in titles:

        normalized = normalize_title(title)

        if not normalized:
            continue

        index.setdefault(normalized, title)
        index.setdefault(singular_form(normalized), title)

    # Token table for every distinct original title
    entries = []
    seen = set()

    for original in index.values():

        if original in seen:
            continue

        seen.add(original)

        normalized = normalize_title(original)

        if normalized:
            entries.append((normalized.split(), original))

    _TOKEN_INDEX["index"] = index
    _TOKEN_INDEX["entries"] = entries

    return index


def tokens_match(cat_token, int_token):
    """Two words match when equal, or when both are long
    enough for one to be a prefix of the other.

    Short words ("a", "as", "ai") must match exactly, so a
    single-letter token can never swallow a whole word.
    """

    if cat_token == int_token:
        return True

    if len(cat_token) >= 3 and len(int_token) >= 3:
        return (int_token.startswith(cat_token) or
                cat_token.startswith(int_token))

    return False


def token_subset_match(catalog_tokens, interest_tokens):
    """True when every catalog word matches some interest word.

    Words match when one is a prefix of the other, so plurals
    still line up ("architect" ~ "architects").
    """

    for cat_token in catalog_tokens:

        if not any(
                tokens_match(cat_token, int_token)
                for int_token in interest_tokens):
            return False

    return True


def resolve_interest_title(title, index):
    """Find the career_interest title matching a catalog title.

    Strategy (in order):
      1. exact normalized / singular match
      2. token-subset match, keeping the closest title by ratio
         (handles "Accountant" -> "Accountants and Auditors",
          "Airline Pilot" -> "Airline Pilots, Copilots, ...")
      3. fuzzy difflib match as a last resort
    """

    normalized = normalize_title(title)

    if not normalized:
        return None

    if normalized in _RESOLVED_TITLE_CACHE:
        return _RESOLVED_TITLE_CACHE[normalized]

    result = None

    # 1) Exact normalized / singular match
    if normalized in index:
        result = index[normalized]

    elif singular_form(normalized) in index:
        result = index[singular_form(normalized)]

    else:
        catalog_tokens = normalized.split()

        entries = None

        if _TOKEN_INDEX["index"] is index:
            entries = _TOKEN_INDEX["entries"]

        # 2) Token-subset match, best ratio wins
        if entries:

            best_ratio = 0.0

            for interest_tokens, original in entries:

                if not token_subset_match(
                        catalog_tokens, interest_tokens):
                    continue

                ratio = SequenceMatcher(
                    None,
                    normalized,
                    " ".join(interest_tokens)
                ).ratio()

                if ratio > best_ratio:
                    best_ratio = ratio
                    result = original

        # 2b) First-word + head-noun fallback when wording
        #     differs everywhere else. BOTH the first word and
        #     the closing word must line up, so random roles
        #     that merely share a head noun are rejected
        #     ("Account Manager" -/ "Range Managers").
        if result is None and len(catalog_tokens) >= 2 and entries:

            first = catalog_tokens[0]
            head = catalog_tokens[-1]
            best_ratio = 0.5

            for interest_tokens, original in entries:

                if len(interest_tokens) < 2:
                    continue

                if not tokens_match(head, interest_tokens[-1]):
                    continue

                # First word must appear too
                first_ok = any(
                    tokens_match(first, token)
                    for token in interest_tokens
                )

                if not first_ok:
                    continue

                ratio = SequenceMatcher(
                    None,
                    normalized,
                    " ".join(interest_tokens)
                ).ratio()

                if ratio > best_ratio:
                    best_ratio = ratio
                    result = original

        # 3) Fuzzy fallback for wording differences
        if result is None:

            candidates = get_close_matches(
                singular_form(normalized),
                list(index.keys()),
                n=1,
                cutoff=0.8
            )

            if candidates:
                result = index[candidates[0]]

    _RESOLVED_TITLE_CACHE[normalized] = result

    return result


# =========================================================
# GET CAREER DATA
# =========================================================

def load_career_data():

    if not os.path.exists(CAREER_DB):
        return []

    conn = sqlite3.connect(CAREER_DB)

    conn.row_factory = sqlite3.Row

    try:
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
    except sqlite3.OperationalError:
        # Table missing (e.g. career.db rebuilt from CSV only)
        rows = []

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

    data = request.get_json(silent=True) or {}

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

        except (TypeError, ValueError):

            return jsonify({
                "success": False,
                "message": "RIASEC scores must be numbers."
            }), 400

    try:

        rows = load_career_data()

        career_profiles = build_career_profiles(
            rows
        )

        if not career_profiles:

            return jsonify({
                "success": False,
                "message":
                    "Career interest data is not available. "
                    "Please contact support."
            }), 503

        # Match every catalog career to its RIASEC profile by
        # normalized title. (A pure O*NET code join drops almost
        # everything: 460 of the 500 catalog careers have no
        # usable code and the two datasets share no titles.)
        title_index = build_interest_title_index(
            career_profiles.keys()
        )

        recommendations = []
        seen_titles = set()

        conn = sqlite3.connect(CAREER_DB)

        catalog_rows = conn.execute("""
            SELECT career_title, onet_soc_code, sector
            FROM careers
            ORDER BY career_title
        """).fetchall()

        conn.close()

        # Pass 1: resolve every catalog career and collect the
        # RIASEC profiles of the direct matches per sector
        sector_scores = {}
        pending = []

        for career_title, onet_code, sector in catalog_rows:

            if not career_title:
                continue

            title_key = career_title.strip().lower()

            if title_key in seen_titles:
                continue

            seen_titles.add(title_key)

            interest_title = resolve_interest_title(
                career_title,
                title_index
            )

            career = career_profiles.get(interest_title)

            scores = (
                career["scores"]
                if career is not None
                else None
            )

            if scores is not None and sector:
                sector_scores.setdefault(
                    sector, []
                ).append(scores)

            pending.append(
                (career_title, onet_code, sector, scores)
            )

        # Sector averages for careers without a direct title
        # match: the role inherits the RIASEC profile of the
        # matched careers in its own sector (only when at
        # least two direct matches back the average up)
        sector_means = {}

        for sector, score_list in sector_scores.items():

            if len(score_list) < 2:
                continue

            sector_means[sector] = {
                key: sum(
                    scores[key] for scores in score_list
                ) / len(score_list)
                for key in ("R", "I", "A", "S", "E", "C")
            }

        # Pass 2: calculate match percentages
        for career_title, onet_code, sector, scores in pending:

            match_type = "title"

            if scores is None:

                scores = sector_means.get(sector)

                # No direct or sector profile: skip instead
                # of inventing a 0% match
                if scores is None:
                    continue

                match_type = "sector"

            match_percentage = calculate_match(
                user_scores,
                scores
            )

            recommendations.append({

                "title":
                    career_title,

                "onet_soc_code":
                    str(onet_code or "").strip(),

                "match":
                    match_percentage,

                "scores":
                    scores,

                "matchType":
                    match_type

            })

        if not recommendations:

            return jsonify({
                "success": False,
                "message":
                    "No career matches could be calculated. "
                    "Please contact support."
            }), 503

        # Highest matches first
        recommendations.sort(
            key=lambda career:
                career["match"],
            reverse=True
        )

        # Return top 10 careers
        recommendations = recommendations[:10]

        # Best effort: store the results with the latest
        # assessment of the logged-in user (Req: persist results)
        try:

            user_db = get_db_connection()

            user_db.execute(
                """
                UPDATE assessments
                SET matches = ?
                WHERE id = (
                    SELECT id
                    FROM assessments
                    WHERE user_id = ?
                    ORDER BY created_at DESC, id DESC
                    LIMIT 1
                )
                """,
                (
                    json.dumps(recommendations),
                    session["user_id"],
                )
            )

            user_db.commit()
            user_db.close()

        except Exception as error:

            print("Save assessment results error:", error)

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

        # 1) Full catalog details from the 500-career dataset
        conn = sqlite3.connect(CAREER_DB)
        conn.row_factory = sqlite3.Row

        catalog_row = conn.execute(
            """
            SELECT *
            FROM careers
            WHERE LOWER(career_title) = LOWER(?)
            """,
            (career_title,)
        ).fetchone()

        conn.close()

        # 2) RIASEC scores from the career_interest dataset
        rows = load_career_data()

        career_profiles = build_career_profiles(
            rows
        )

        selected_career = None

        for title, career in career_profiles.items():

            if title.lower() == career_title.lower():

                selected_career = career
                break

        # The two datasets word titles differently, so fall
        # back to the normalized/fuzzy title matcher
        if selected_career is None:

            title_index = build_interest_title_index(
                career_profiles.keys()
            )

            interest_title = resolve_interest_title(
                career_title,
                title_index
            )

            if interest_title is not None:

                selected_career = career_profiles.get(
                    interest_title
                )

        if catalog_row is None and selected_career is None:

            return jsonify({
                "success": False,
                "message": "Career not found."
            }), 404

        career = {}

        if catalog_row is not None:

            career = {
                "careerId":
                    catalog_row["career_id"],
                "careerTitle":
                    catalog_row["career_title"],
                "title":
                    catalog_row["career_title"],
                "sector":
                    catalog_row["sector"],
                "shortDescription":
                    catalog_row["short_description"],
                "importantSkills":
                    catalog_row["important_skills"],
                "educationQualification":
                    catalog_row["education_qualification"],
                "recommendedCourses":
                    catalog_row["recommended_courses"],
                "salaryRange":
                    catalog_row["salary_range"],
                "demandLevel":
                    catalog_row["demand_level"],
                "careerRoadmap":
                    catalog_row["career_roadmap"],
                "commonJobRoles":
                    catalog_row["common_job_roles"],
                "careerGrowth":
                    catalog_row["career_growth"],
                "onetSocCode":
                    catalog_row["onet_soc_code"]
            }

        else:

            career = {
                "careerId": None,
                "careerTitle":
                    selected_career["title"],
                "title":
                    selected_career["title"],
                "sector": None,
                "shortDescription": None,
                "importantSkills": None,
                "educationQualification": None,
                "recommendedCourses": None,
                "salaryRange": None,
                "demandLevel": None,
                "careerRoadmap": None,
                "commonJobRoles": None,
                "careerGrowth": None,
                "onetSocCode":
                    selected_career["onet_soc_code"]
            }

        career["scores"] = (
            selected_career["scores"]
            if selected_career is not None
            else None
        )

        return jsonify({
            "success": True,
            "career": career
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

        conn = sqlite3.connect(CAREER_DB)
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT
                career_id,
                career_title,
                sector,
                short_description,
                important_skills,
                education_qualification,
                recommended_courses,
                salary_range,
                demand_level,
                career_roadmap,
                common_job_roles,
                career_growth,
                onet_soc_code
            FROM careers
            WHERE LOWER(career_title) IN (?, ?)
        """, (
            first_title.lower(),
            second_title.lower()
        )).fetchall()

        conn.close()


        first_career = None
        second_career = None


        for row in rows:

            title = row["career_title"]

            if title.lower() == first_title.lower():
                first_career = row

            elif title.lower() == second_title.lower():
                second_career = row


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


        def career_to_dict(row):

            return {
                "careerId":
                    row["career_id"],

                "careerTitle":
                    row["career_title"],

                "sector":
                    row["sector"],

                "shortDescription":
                    row["short_description"],

                "importantSkills":
                    row["important_skills"],

                "educationQualification":
                    row["education_qualification"],

                "recommendedCourses":
                    row["recommended_courses"],

                "salaryRange":
                    row["salary_range"],

                "demandLevel":
                    row["demand_level"],

                "careerRoadmap":
                    row["career_roadmap"],

                "commonJobRoles":
                    row["common_job_roles"],

                "careerGrowth":
                    row["career_growth"],

                "onetSocCode":
                    row["onet_soc_code"]
            }


        return jsonify({

            "success": True,

            "careers": [

                career_to_dict(
                    first_career
                ),

                career_to_dict(
                    second_career
                )

            ]

        })


    except Exception as error:

        print(
            "Compare careers error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to compare careers."
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

    # =========================================================
# 500 CAREER CATALOG API
# =========================================================

@careers_bp.route(
    "/api/career-catalog",
    methods=["GET"]
)
def get_career_catalog():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    try:

        conn = sqlite3.connect(CAREER_DB)
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT
                career_id,
                career_title,
                sector,
                short_description,
                important_skills,
                education_qualification,
                recommended_courses,
                salary_range,
                demand_level,
                career_roadmap,
                common_job_roles,
                career_growth,
                onet_soc_code
            FROM careers
            ORDER BY career_title ASC
        """).fetchall()

        conn.close()

        careers = []

        for row in rows:

            careers.append({
                "careerId": row["career_id"],
                "careerTitle": row["career_title"],
                "sector": row["sector"],
                "shortDescription": row["short_description"],
                "importantSkills": row["important_skills"],
                "educationQualification": row["education_qualification"],
                "recommendedCourses": row["recommended_courses"],
                "salaryRange": row["salary_range"],
                "demandLevel": row["demand_level"],
                "careerRoadmap": row["career_roadmap"],
                "commonJobRoles": row["common_job_roles"],
                "careerGrowth": row["career_growth"],
                "onetSocCode": row["onet_soc_code"]
            })

        return jsonify({
            "success": True,
            "count": len(careers),
            "careers": careers
        })

    except Exception as error:

        print(
            "Career catalog error:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to load career catalog."
        }), 500    