"""
test_scorer.py: Unit tests for auditable match score calculation.
Verifies exact calculation:
  skill_score = min(student_level / required_level, 1.0)
  match_score = round(average(skill_scores) * 100, 1)
"""

from skilltrace_ai.scorer import calculate_match_score


def test_prompt_benchmark_example():
    """
    Verifies the exact benchmark calculation from the SIH requirements:
      Python: student=4, req=4 -> 1.0
      SQL: student=3, req=4 -> 0.75
      Power BI: student=0, req=3 -> 0.0
      Score: (1 + 0.75 + 0) / 3 * 100 = 58.3%
    """
    evaluated_skills = [
        {"name": "Python", "student_level": 4, "required_level": 4},
        {"name": "SQL", "student_level": 3, "required_level": 4},
        {"name": "Power BI", "student_level": 0, "required_level": 3},
    ]

    result = calculate_match_score(evaluated_skills)
    assert result["match_score"] == 58.3
    assert result["total_required_skills"] == 3

    breakdown = result["breakdown"]
    assert breakdown[0]["ratio"] == 1.0
    assert breakdown[1]["ratio"] == 0.75
    assert breakdown[2]["ratio"] == 0.0


def test_perfect_match():
    evaluated_skills = [
        {"name": "Python", "student_level": 4, "required_level": 4},
        {"name": "SQL", "student_level": 4, "required_level": 4},
    ]
    result = calculate_match_score(evaluated_skills)
    assert result["match_score"] == 100.0


def test_zero_match():
    evaluated_skills = [
        {"name": "Python", "student_level": 0, "required_level": 4},
        {"name": "SQL", "student_level": 0, "required_level": 4},
    ]
    result = calculate_match_score(evaluated_skills)
    assert result["match_score"] == 0.0


def test_student_exceeds_requirement_capped_at_one():
    evaluated_skills = [
        {"name": "Python", "student_level": 5, "required_level": 3},
    ]
    result = calculate_match_score(evaluated_skills)
    assert result["match_score"] == 100.0
    assert result["breakdown"][0]["ratio"] == 1.0


def test_empty_evaluated_skills():
    result = calculate_match_score([])
    assert result["match_score"] == 0.0
    assert result["total_required_skills"] == 0
