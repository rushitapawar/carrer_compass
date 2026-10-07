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

    data = request.get_json()

    answers = data.get("answers", [])

    if len(answers) != 25:
        return jsonify({
            "success": False,
            "message": "Exactly 25 answers are required."
        }), 400

    scores = {
        "R": 0,
        "I": 0,
        "A": 0,
        "S": 0,
        "E": 0,
        "C": 0
    }

    for question_index, answer in enumerate(answers):

        if not isinstance(answer, int):
            return jsonify({
                "success": False,
                "message": "Answers must contain numbers only."
            }), 400

        if answer < 0 or answer > 3:
            return jsonify({
                "success": False,
                "message": "Each answer must be between 0 and 3."
            }), 400

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

    return jsonify({
        "success": True,
        "scores": scores,
        "topTypes": top_types
    })