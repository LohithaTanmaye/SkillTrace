"""
test_pipeline.py: End-to-end integration tests for the skilltrace_ai pipeline.
Tests full flow:
  Student answers assessment -> analyze_assessment() -> assessment_to_student_skills()
  -> analyze_student() -> score + matched + gaps + recommendations + explanation
"""

import pytest
from skilltrace_ai import (
    analyze_student,
    analyze_assessment,
    assessment_to_student_skills,
)


def test_full_sih_benchmark_flow():
    # 1. Assessment step
    assessment_input = {
        "assessment": [
            {"skill": "Python", "questions": 10, "correct_answers": 8},   # 80% -> Level 4
            {"skill": "SQL", "questions": 10, "correct_answers": 6},      # 60% -> Level 3
            # Power BI not taken / missing
        ]
    }

    assessment_res = analyze_assessment(assessment_input)
    assert len(assessment_res["evaluated_skills"]) == 2

    # 2. Conversion to student skills profile
    student_skills = assessment_to_student_skills(assessment_res["evaluated_skills"])
    assert len(student_skills) == 2
    assert student_skills[0] == {"name": "Python", "level": 4}
    assert student_skills[1] == {"name": "SQL", "level": 3}

    # 3. Target job benchmark
    job_skills = [
        {"name": "Python", "required_level": 4},
        {"name": "SQL", "required_level": 4},
        {"name": "Power BI", "required_level": 3},
    ]

    # 4. Run full analysis
    analysis_payload = {
        "student_skills": student_skills,
        "job_skills": job_skills,
        "job_title": "Junior Data Analyst",
    }
    result = analyze_student(analysis_payload)

    # 5. Verify computed score: (1.0 + 0.75 + 0.0) / 3 * 100 = 58.3%
    assert result["match_score"] == 58.3

    # Verify 3-tier gap breakdown
    matched_names = [s["name"] for s in result["matched_skills"]]
    partial_names = [s["name"] for s in result["partial_gaps"]]
    missing_names = [s["name"] for s in result["missing_skills"]]

    assert "Python" in matched_names
    assert "SQL" in partial_names
    assert "Power BI" in missing_names

    # Verify recommendations generated
    assert len(result["recommendations"]) >= 2

    # Verify mandatory ethical disclaimer
    assert "does not guarantee job suitability or employment" in result["disclaimer"]
    assert "estimate of skill alignment" in result["disclaimer"]

    # Verify explainable summary text
    explanation = result["explanation"]
    assert "Python" in explanation
    assert "SQL" in explanation
    assert "Power BI" in explanation


def test_pipeline_validation_errors():
    with pytest.raises(ValueError):
        analyze_student("invalid_string_input")

    with pytest.raises(ValueError):
        analyze_student({"student_skills": "not_a_list", "job_skills": []})

    with pytest.raises(ValueError):
        analyze_student({"student_skills": [], "job_skills": "not_a_list"})
