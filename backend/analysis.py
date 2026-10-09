"""Career analysis: RIASEC scoring + career recommendation (modular).

The recommendation strategy is intentionally self-contained so it can be
improved later without touching any API module:

1. questionnaire answers (list of ints 0-3) -> RIASEC interest scores
2. scores -> sector affinity profile (SECTOR_AFFINITY)
3. every career scored against the profile -> match percentage

No fake data is used: careers are always loaded from the careers table,
which is seeded from the project CSV.
"""

from database import CAREER_SELECT, get_db

RIASEC_TYPES = ("R", "I", "A", "S", "E", "C")

# Every question maps its 4 options (indexes 0-3) to RIASEC types.
QUESTION_MAPPING = [
    ["R", "S", "A", "E"],
    ["I", "A", "S", "C"],
    ["E", "R", "I", "A"],
    ["S", "C", "E", "R"],
    ["A", "I", "S", "E"],
    ["R", "I", "C", "A"],
    ["S", "E", "A", "I"],
    ["C", "R", "I", "E"],
    ["A", "S", "E", "R"],
    ["I", "C", "R", "A"],
    ["E", "S", "C", "I"],
    ["R", "A", "I", "E"],
    ["S", "I", "A", "C"],
    ["E", "R", "S", "C"],
    ["A", "I", "E", "R"],
    ["C", "S", "R", "A"],
    ["I", "E", "A", "S"],
    ["R", "C", "I", "E"],
    ["S", "A", "E", "I"],
    ["E", "C", "R", "S"],
    ["A", "R", "I", "C"],
    ["I", "S", "E", "A"],
    ["R", "E", "C", "I"],
    ["S", "A", "I", "E"],
    ["C", "R", "E", "S"],
]

QUESTION_COUNT = len(QUESTION_MAPPING)  # 25

# Affinity of each CSV sector with the six RIASEC interest types (0..1).
# Weights are normalized before matching; sectors are the exact 33 values
# present in career_compass_500_careers.csv.
SECTOR_AFFINITY = {
    "Accounting & Taxation": {"C": 0.9, "E": 0.4, "I": 0.3},
    "Agriculture & Environmental Sciences": {"R": 0.8, "I": 0.7, "S": 0.3},
    "Architecture & Construction": {"R": 0.7, "A": 0.6, "I": 0.5},
    "Artificial Intelligence & Machine Learning": {"I": 0.9, "C": 0.5, "R": 0.3},
    "Aviation & Aerospace": {"R": 0.8, "I": 0.7, "C": 0.4},
    "Beauty, Fashion & Lifestyle": {"A": 0.8, "S": 0.5, "E": 0.4},
    "Business & Management": {"E": 0.9, "C": 0.5, "I": 0.4},
    "Cloud Computing & DevOps": {"I": 0.8, "C": 0.6, "R": 0.3},
    "Cybersecurity": {"I": 0.8, "R": 0.5, "C": 0.5},
    "Data Science & Analytics": {"I": 0.9, "C": 0.6, "A": 0.2},
    "Design, UI/UX & Creative": {"A": 0.9, "I": 0.5, "E": 0.3},
    "Education & Teaching": {"S": 0.9, "I": 0.6, "A": 0.4},
    "Engineering": {"R": 0.8, "I": 0.7, "C": 0.3},
    "Finance, Banking & Investment": {"C": 0.8, "E": 0.7, "I": 0.5},
    "Food, Nutrition & Culinary": {"R": 0.6, "A": 0.5, "S": 0.4},
    "Government & Public Services": {"C": 0.7, "S": 0.6, "E": 0.5},
    "Healthcare & Medicine": {"S": 0.8, "I": 0.8, "R": 0.4},
    "Hospitality, Tourism & Travel": {"S": 0.8, "E": 0.6, "A": 0.4},
    "Human Resources": {"S": 0.8, "E": 0.6, "C": 0.5},
    "Law & Legal Services": {"I": 0.7, "E": 0.6, "C": 0.6},
    "Logistics & Supply Chain": {"C": 0.8, "E": 0.5, "R": 0.4},
    "Manufacturing & Operations": {"R": 0.9, "C": 0.5, "E": 0.3},
    "Marketing & Digital Marketing": {"E": 0.8, "A": 0.7, "S": 0.3},
    "Media, Content & Communication": {"A": 0.9, "S": 0.5, "E": 0.4},
    "Pharmaceutical & Biotechnology": {"I": 0.9, "R": 0.4, "C": 0.4},
    "Real Estate & Infrastructure": {"E": 0.8, "R": 0.5, "C": 0.4},
    "Retail & E-commerce": {"E": 0.7, "C": 0.6, "S": 0.3},
    "Sales & Business Development": {"E": 0.9, "S": 0.6, "C": 0.3},
    "Science & Research": {"I": 0.9, "R": 0.5, "A": 0.3},
    "Social Work & NGO": {"S": 0.9, "E": 0.5, "A": 0.4},
    "Software & Web Development": {"I": 0.8, "A": 0.5, "C": 0.4},
    "Sports & Fitness": {"R": 0.8, "S": 0.5, "E": 0.3},
    "Technology & IT": {"I": 0.8, "C": 0.5, "R": 0.4},
}

DEFAULT_AFFINITY = {"I": 0.5, "E": 0.4, "S": 0.4, "A": 0.3, "C": 0.3, "R": 0.3}


class AnswerError(ValueError):
    """Raised when questionnaire answers are invalid (maps to HTTP 400)."""


def validate_answers(answers):
    """Validate the answers list: 25 integers, each between 0 and 3."""
    if not isinstance(answers, list) or not answers:
        raise AnswerError("Answers must be a non-empty list.")
    if len(answers) != QUESTION_COUNT:
        raise AnswerError(f"Please complete all {QUESTION_COUNT} questions.")
    for index, answer in enumerate(answers):
        if isinstance(answer, bool) or not isinstance(answer, int):
            raise AnswerError(f"Answer {index + 1} must be a whole number.")
        if answer < 0 or answer > 3:
            raise AnswerError(f"Answer {index + 1} must be between 0 and 3.")


def compute_scores(answers):
    """Turn questionnaire answers into RIASEC counts."""
    validate_answers(answers)
    scores = {letter: 0 for letter in RIASEC_TYPES}
    for question_index, answer in enumerate(answers):
        scores[QUESTION_MAPPING[question_index][answer]] += 1
    return scores


def top_types(scores, count=3):
    """Return the strongest RIASEC types (most points first)."""
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [letter for letter, points in ordered[:count] if points > 0]


def _normalized(scores):
    """Normalize scores so values sum to 1 (all-zero handled safely)."""
    total = float(sum(scores.values()))
    if total <= 0:
        share = 1.0 / len(RIASEC_TYPES)
        return {letter: share for letter in RIASEC_TYPES}
    return {letter: scores.get(letter, 0) / total for letter in RIASEC_TYPES}


def _sector_affinity(sector):
    """Return normalized affinity weights for a sector."""
    raw = dict(SECTOR_AFFINITY.get(sector, DEFAULT_AFFINITY))
    for letter in RIASEC_TYPES:
        raw.setdefault(letter, 0.0)
    return _normalized(raw)


def match_percentage(user_scores, sector):
    """Similarity (0-100) between normalized user scores and a sector profile."""
    user = _normalized(user_scores)
    affinity = _sector_affinity(sector)
    difference = sum(abs(user[letter] - affinity[letter]) for letter in RIASEC_TYPES)
    similarity = 1 - (difference / 2)
    return round(similarity * 100)


def recommend(answers=None, scores=None, limit=10):
    """Recommend the careers that best match the user's interests.

    Provide either raw questionnaire `answers` or precomputed `scores`.
    Returns a list of career dicts (full records) with match_percentage.
    """
    if scores is None:
        scores = compute_scores(answers)

    try:
        limit = max(1, min(int(limit), 50))
    except (TypeError, ValueError):
        limit = 10

    with get_db() as conn:
        rows = conn.execute(
            f"SELECT {CAREER_SELECT} FROM careers"
        ).fetchall()

    recommendations = []
    for row in rows:
        career = dict(row)
        career["match_percentage"] = match_percentage(scores, career["sector"])
        recommendations.append(career)

    recommendations.sort(
        key=lambda career: (career["match_percentage"], career["career_title"]),
        reverse=True,
    )
    return recommendations[:limit]


def analyze(answers, limit=10):
    """Full analysis result: scores, top types and career recommendations."""
    scores = compute_scores(answers)
    return {
        "riasec_scores": scores,
        "top_types": top_types(scores),
        "recommendations": recommend(scores=scores, limit=limit),
    }
