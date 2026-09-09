"""
test_assessment.py: Unit tests for assessment evaluation and boundary value mapping.
Verifies strict inclusive boundaries:
  20%  -> Level 1 (Beginner)
  40%  -> Level 2 (Basic)
  60%  -> Level 3 (Intermediate)
  80%  -> Level 4 (Advanced)
  100% -> Level 5 (Proficient)
"""

import pytest
from skilltrace_ai.assessment import (
    percentage_to_level,
    analyze_assessment,
    assessment_to_student_skills,
)


def test_strict_boundary_values():
    # 0% - 20% inclusive -> Level 1
    assert percentage_to_level(0.0) == (1, "Beginner")
    assert percentage_to_level(15.0) == (1, "Beginner")
    assert percentage_to_level(20.0) == (1, "Beginner")

    # >20% - 40% inclusive -> Level 2
    assert percentage_to_level(20.1) == (2, "Basic")
    assert percentage_to_level(30.0) == (2, "Basic")
    assert percentage_to_level(40.0) == (2, "Basic")

    # >40% - 60% inclusive -> Level 3
    assert percentage_to_level(40.1) == (3, "Intermediate")
    assert percentage_to_level(50.0) == (3, "Intermediate")
    assert percentage_to_level(60.0) == (3, "Intermediate")

    # >60% - 80% inclusive -> Level 4
    assert percentage_to_level(60.1) == (4, "Advanced")
    assert percentage_to_level(70.0) == (4, "Advanced")
    assert percentage_to_level(80.0) == (4, "Advanced")

    # >80% - 100% inclusive -> Level 5
    assert percentage_to_level(80.1) == (5, "Proficient")
    assert percentage_to_level(90.0) == (5, "Proficient")
    assert percentage_to_level(100.0) == (5, "Proficient")


def test_analyze_assessment_standard():
    payload = {
        "assessment": [
            {"skill": "Python", "questions": 10, "correct_answers": 8},   # 80% -> Level 4
            {"skill": "SQL", "questions": 10, "correct_answers": 6},      # 60% -> Level 3
            {"skill": "Power BI", "questions": 10, "correct_answers": 2}, # 20% -> Level 1
        ]
    }
    result = analyze_assessment(payload)
    evaluated = result["evaluated_skills"]
    assert len(evaluated) == 3

    python_item = next(item for item in evaluated if item["skill"] == "Python")
    assert python_item["percentage"] == 80.0
    assert python_item["estimated_level"] == 4
    assert python_item["proficiency_label"] == "Advanced"

    sql_item = next(item for item in evaluated if item["skill"] == "SQL")
    assert sql_item["percentage"] == 60.0
    assert sql_item["estimated_level"] == 3

    pbi_item = next(item for item in evaluated if item["skill"] == "Power BI")
    assert pbi_item["percentage"] == 20.0
    assert pbi_item["estimated_level"] == 1


def test_assessment_to_student_skills_transformation():
    evaluated_output = [
        {"skill": "Python", "estimated_level": 4},
        {"skill": "SQL", "estimated_level": 3},
        {"skill": "Power BI", "estimated_level": 1},
    ]
    student_skills = assessment_to_student_skills(evaluated_output)
    assert len(student_skills) == 3
    assert student_skills[0] == {"name": "Python", "level": 4}
    assert student_skills[1] == {"name": "SQL", "level": 3}
    assert student_skills[2] == {"name": "Power BI", "level": 1}


def test_assessment_invalid_inputs():
    # Negative correct answers
    with pytest.raises(ValueError):
        analyze_assessment({"assessment": [{"skill": "Python", "questions": 10, "correct_answers": -1}]})

    # Correct answers > questions
    with pytest.raises(ValueError):
        analyze_assessment({"assessment": [{"skill": "Python", "questions": 10, "correct_answers": 11}]})

    # Zero questions
    with pytest.raises(ValueError):
        analyze_assessment({"assessment": [{"skill": "Python", "questions": 0, "correct_answers": 0}]})

    # Malformed non-list assessment
    with pytest.raises(ValueError):
        analyze_assessment({"assessment": "invalid_string"})
