from flask import Blueprint, request, jsonify, session


analysis_bp = Blueprint(
    "analysis",
    __name__
)


# Each question maps its 4 options to RIASEC types.
# Answers are numeric: 0, 1, 2, 3.

QUESTION_MAPPING = [

    # Q1
    ["R", "S", "A", "E"],

    # Q2
    ["I", "A", "S", "C"],

    # Q3
    ["E", "R", "I", "A"],

    # Q4
    ["S", "C", "E", "R"],

    # Q5
    ["A", "I", "S", "E"],

    # Q6
    ["R", "I", "C", "A"],

    # Q7
    ["S", "E", "A", "I"],

    # Q8
    ["C", "R", "I", "E"],

    # Q9
    ["A", "S", "E", "R"],

    # Q10
    ["I", "C", "R", "A"],

    # Q11
    ["E", "S", "C", "I"],

    # Q12
    ["R", "A", "I", "E"],

    # Q13
    ["S", "I", "A", "C"],

    # Q14
    ["E", "R", "S", "C"],

    # Q15
    ["A", "I", "E", "R"],

    # Q16
    ["C", "S", "R", "A"],

    # Q17
    ["I", "E", "A", "S"],

    # Q18
    ["R", "C", "I", "E"],

    # Q19
    ["S", "A", "E", "I"],

    # Q20
    ["E", "C", "R", "S"],

    # Q21
    ["A", "R", "I", "C"],

    # Q22
    ["I", "S", "E", "A"],

    # Q23
    ["R", "E", "C", "I"],

    # Q24
    ["S", "A", "I", "E"],

    # Q25
    ["C", "R", "E", "S"]
]


def score_answers(answers):
    """Map the 25 numeric answers to RIASEC scores.

    Shared by /api/analyze-assessment and the assessment save
    endpoint so results are always calculated the same way.

    Returns (scores, top_types).
    Raises ValueError with a user-facing message when invalid.
    """

    if not isinstance(answers, list) or len(answers) != 25:
        raise ValueError("Exactly 25 answers are required.")

    scores = {
        "R": 0,
        "I": 0,
        "A": 0,
        "S": 0,
        "E": 0,
        "C": 0
    }

    for question_index, answer in enumerate(answers):

        if not isinstance(answer, int) or isinstance(answer, bool):
            raise ValueError("Answers must contain numbers only.")

        if answer < 0 or answer > 3:
            raise ValueError("Each answer must be between 0 and 3.")

        riasec_type = QUESTION_MAPPING[
            question_index
        ][answer]

        scores[riasec_type] += 1

    sorted_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top_types = [
        item[0]
        for item in sorted_scores[:3]
    ]

    return scores, top_types


@analysis_bp.route(
    "/api/analyze-assessment",
    methods=["POST"]
)
def analyze_assessment():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(silent=True) or {}

    answers = data.get("answers", [])

    try:
        scores, top_types = score_answers(answers)

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    return jsonify({
        "success": True,
        "scores": scores,
        "topTypes": top_types
    })